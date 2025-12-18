"""
Multi-tenant executions router with SQLAlchemy.

This router handles execution queries for the authenticated organization.
Uses SQLAlchemy for database operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from typing import List, Optional, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import structlog
import asyncio
import json
import uuid as uuid_module

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func

from control_plane_api.app.middleware.auth import get_current_organization
from control_plane_api.app.database import get_db
from control_plane_api.app.lib.sqlalchemy_utils import model_to_dict, models_to_dict_list
from control_plane_api.app.lib.temporal_client import get_temporal_client
from control_plane_api.app.lib.redis_client import get_redis_client
from control_plane_api.app.workflows.agent_execution import AgentExecutionWorkflow
from control_plane_api.app.services.agno_service import agno_service
from control_plane_api.app.models.execution import Execution
from control_plane_api.app.models.job import Job, JobExecution
from control_plane_api.app.models.agent import Agent
from control_plane_api.app.models.team import Team
from control_plane_api.app.models.worker import WorkerQueue
from control_plane_api.app.models.associations import ExecutionParticipant
from control_plane_api.app.models.session import Session as SessionModel

logger = structlog.get_logger()

router = APIRouter()


def sanitize_jsonb_field(value: Any, field_name: str = None) -> dict:
    """Sanitize a JSONB field value to ensure it's a valid dict."""
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    return {}


async def validate_job_exists(
    db: Session,
    job_id: str,
    organization_id: str,
    logger_context: dict = None
) -> dict:
    """
    Validate that a job exists and belongs to the organization.

    Args:
        db: SQLAlchemy session
        job_id: Job ID to validate
        organization_id: Organization ID for security check
        logger_context: Additional context for logging

    Returns:
        dict: Job record if valid

    Raises:
        HTTPException: 404 if not found, 410 if deleted
    """
    # Log validation attempt
    logger.info(
        "validating_job_existence",
        job_id=job_id,
        organization_id=organization_id,
        **(logger_context or {})
    )

    try:
        job_obj = db.query(Job).filter(
            Job.id == job_id,
            Job.organization_id == organization_id
        ).first()

        # Check if result exists
        if not job_obj:
            logger.error(
                "job_not_found_validation_failed",
                job_id=job_id,
                organization_id=organization_id,
                **(logger_context or {})
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found or does not belong to organization"
            )

        job = model_to_dict(job_obj)

        # Check if job is in deleted/inactive state
        if job_obj.status == "deleted":
            logger.error(
                "job_deleted_validation_failed",
                job_id=job_id,
                job_name=job_obj.name,
                **(logger_context or {})
            )
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail=f"Job {job_id} has been deleted"
            )

        logger.info(
            "job_validation_successful",
            job_id=job_id,
            job_name=job_obj.name,
            job_enabled=job_obj.enabled,
        )

        return job

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "job_validation_error",
            job_id=job_id,
            error=str(e),
            **(logger_context or {})
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate job: {str(e)}"
        )


# Pydantic schemas
class ParticipantResponse(BaseModel):
    """Participant in an execution"""
    id: str
    user_id: str
    user_name: str | None
    user_email: str | None
    user_avatar: str | None
    role: str
    joined_at: str
    last_active_at: str


class ExecutionResponse(BaseModel):
    id: str
    organization_id: str
    execution_type: str
    entity_id: str
    entity_name: str | None
    prompt: str
    system_prompt: str | None
    status: str
    response: str | None
    error_message: str | None
    usage: dict
    execution_metadata: dict
    runner_name: str | None
    user_id: str | None
    user_name: str | None
    user_email: str | None
    user_avatar: str | None
    created_at: str
    started_at: str | None
    completed_at: str | None
    updated_at: str
    participants: List[ParticipantResponse] = Field(default_factory=list)


# Worker-specific endpoints for job execution tracking


class CreateExecutionRecordRequest(BaseModel):
    """Request model for creating execution records from workers"""
    execution_id: str
    job_id: Optional[str] = None
    organization_id: str
    entity_type: str  # "agent" or "team"
    entity_id: Optional[str] = None
    prompt: str
    trigger_type: str  # "cron", "webhook", "manual"
    trigger_metadata: dict


class UpdateJobExecutionStatusRequest(BaseModel):
    """Request model for updating job execution status"""
    status: str
    duration_ms: Optional[int] = None
    error_message: Optional[str] = None


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_execution_record(
    request_data: CreateExecutionRecordRequest,
    request: Request,
    organization: dict = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    """
    Create execution and job_executions records for scheduled jobs.

    This endpoint is used by workers to create execution records via HTTP
    instead of directly accessing the database.
    """
    try:
        from croniter import croniter

        now = datetime.now(timezone.utc)

        # Enhanced logging for debugging stale job_id sources
        logger.info(
            "execution_request_received",
            execution_id=request_data.execution_id,
            job_id=request_data.job_id,
            trigger_type=request_data.trigger_type,
            organization_id=request_data.organization_id,
            endpoint=request.url.path,
            source_headers={
                "temporal_workflow": request.headers.get("X-Temporal-Workflow-Id"),
                "temporal_run": request.headers.get("X-Temporal-Run-Id"),
            },
        )

        # Get entity name for display using SQLAlchemy
        entity_name = None
        runner_name = None

        if request_data.entity_id and request_data.entity_type:
            try:
                if request_data.entity_type == "agent":
                    entity = db.query(Agent).filter(Agent.id == request_data.entity_id).first()
                elif request_data.entity_type == "team":
                    entity = db.query(Team).filter(Team.id == request_data.entity_id).first()
                else:
                    entity = None
                if entity:
                    entity_name = entity.name
                    runner_name = getattr(entity, 'runner_name', None)
            except Exception as e:
                logger.warning(
                    "failed_to_get_entity_name",
                    entity_type=request_data.entity_type,
                    entity_id=request_data.entity_id,
                    error=str(e)
                )

        # If runner_name is still None, try to get it from the job's worker_queue_name
        if runner_name is None and request_data.job_id:
            try:
                job = db.query(Job).filter(Job.id == request_data.job_id).first()
                if job and job.worker_queue_name:
                    worker_queue_name = job.worker_queue_name
                    # Extract runner_name from worker_queue_name (format: "org_id.runner_name")
                    runner_name = worker_queue_name.split(".")[-1] if "." in worker_queue_name else worker_queue_name
                    logger.info(
                        "extracted_runner_name_from_job",
                        job_id=request_data.job_id,
                        worker_queue_name=worker_queue_name,
                        runner_name=runner_name
                    )
            except Exception as e:
                logger.warning(
                    "failed_to_get_runner_name_from_job",
                    job_id=request_data.job_id,
                    error=str(e)
                )

        # If runner_name is still None, use a default value
        # This can happen for jobs with AUTO/ENVIRONMENT executor types
        if runner_name is None:
            runner_name = "auto"
            logger.info(
                "using_default_runner_name",
                execution_id=request_data.execution_id,
                job_id=request_data.job_id,
                runner_name=runner_name
            )

        # Map trigger_type to trigger_source
        trigger_source_map = {
            "manual": "job_manual",
            "cron": "job_cron",
            "webhook": "job_webhook",
        }
        trigger_source = trigger_source_map.get(request_data.trigger_type, "job_cron")

        # Determine execution_type
        execution_type_value = request_data.entity_type.upper() if request_data.entity_type else "AGENT"

        # Create execution record using SQLAlchemy
        execution = Execution(
            id=uuid_module.UUID(request_data.execution_id),
            organization_id=request_data.organization_id,
            execution_type=execution_type_value,
            entity_id=uuid_module.UUID(request_data.entity_id) if request_data.entity_id else None,
            entity_name=entity_name,
            runner_name=runner_name,
            trigger_source=trigger_source,
            trigger_metadata={
                "job_id": request_data.job_id,
                "job_name": request_data.trigger_metadata.get("job_name"),
                "trigger_type": request_data.trigger_type,
                **request_data.trigger_metadata,
            },
            user_id=request_data.trigger_metadata.get("user_id"),
            user_email=request_data.trigger_metadata.get("user_email"),
            user_name=request_data.trigger_metadata.get("user_name"),
            user_avatar=request_data.trigger_metadata.get("user_avatar"),
            status="pending",
            prompt=request_data.prompt,
            created_at=now,
            updated_at=now,
            execution_metadata={
                "job_id": request_data.job_id,
                "job_name": request_data.trigger_metadata.get("job_name"),
                "trigger_type": request_data.trigger_type,
                "scheduled_execution": True,
                **request_data.trigger_metadata,
            },
        )
        db.add(execution)
        db.commit()

        logger.info(
            "created_execution_record",
            execution_id=request_data.execution_id,
            job_id=request_data.job_id,
        )

        # Publish job_started event to Redis for real-time UI updates
        try:
            redis_client = get_redis_client()
            if redis_client:
                event_data = {
                    "event_type": "run_started",
                    "data": {
                        "job_id": request_data.job_id,
                        "execution_id": request_data.execution_id,
                        "status": "pending",
                        "trigger_type": request_data.trigger_type,
                        "message": f"Job execution started",
                        "entity_type": request_data.entity_type,
                        "entity_id": request_data.entity_id,
                    },
                    "timestamp": now,
                    "execution_id": request_data.execution_id,
                }

                # Push to Redis list
                redis_key = f"execution:{request_data.execution_id}:events"
                await redis_client.lpush(redis_key, json.dumps(event_data))
                await redis_client.ltrim(redis_key, 0, 999)
                await redis_client.expire(redis_key, 3600)

                # Publish to pub/sub for real-time streaming
                pubsub_channel = f"execution:{request_data.execution_id}:stream"
                await redis_client.publish(pubsub_channel, json.dumps(event_data))

                logger.info(
                    "job_started_event_published",
                    execution_id=request_data.execution_id[:8],
                    job_id=request_data.job_id[:8] if request_data.job_id else None,
                )
        except Exception as event_error:
            # Don't fail the request if event publishing fails
            logger.warning(
                "failed_to_publish_job_started_event",
                execution_id=request_data.execution_id,
                error=str(event_error),
            )

        # Create job_executions junction record if job_id provided
        if request_data.job_id:
            # VALIDATION: Ensure job exists and belongs to organization
            job = await validate_job_exists(
                db=db,
                job_id=request_data.job_id,
                organization_id=request_data.organization_id,
                logger_context={
                    "execution_id": request_data.execution_id,
                    "trigger_type": request_data.trigger_type,
                    "source": "create_execution_record",
                    "trigger_metadata": request_data.trigger_metadata,
                }
            )

            logger.info(
                "creating_job_execution_junction",
                job_id=request_data.job_id,
                job_name=job.get("name"),
                execution_id=request_data.execution_id,
                organization_id=request_data.organization_id,
                trigger_type=request_data.trigger_type,
            )

            try:
                job_execution = JobExecution(
                    id=str(uuid_module.uuid4()),
                    job_id=request_data.job_id,
                    execution_id=uuid_module.UUID(request_data.execution_id),
                    organization_id=request_data.organization_id,
                    trigger_type=request_data.trigger_type,
                    trigger_metadata=request_data.trigger_metadata,
                    execution_status="pending",
                    created_at=now,
                )
                db.add(job_execution)
                db.commit()
                logger.info(
                    "job_execution_junction_created",
                    job_id=request_data.job_id,
                    execution_id=request_data.execution_id,
                )
            except Exception as insert_error:
                db.rollback()
                logger.error(
                    "job_execution_junction_insert_failed",
                    job_id=request_data.job_id,
                    execution_id=request_data.execution_id,
                    error=str(insert_error),
                    error_type=type(insert_error).__name__,
                )
                # Don't raise - junction record is supplementary
                # Execution record already created successfully

            # Update job's last_execution_id and increment total_executions
            try:
                # Get job details to calculate next execution using SQLAlchemy
                job_obj = db.query(Job).filter(Job.id == request_data.job_id).first()

                if job_obj:
                    job_obj.last_execution_id = uuid_module.UUID(request_data.execution_id)
                    job_obj.last_execution_at = now
                    job_obj.total_executions = (job_obj.total_executions or 0) + 1

                    # Calculate next_execution_at for cron jobs
                    if job_obj.trigger_type == "cron" and job_obj.cron_schedule:
                        cron_iter = croniter(job_obj.cron_schedule, datetime.now(timezone.utc))
                        next_execution = cron_iter.get_next(datetime)
                        job_obj.next_execution_at = next_execution

                        logger.info(
                            "calculated_next_execution_time",
                            job_id=request_data.job_id,
                            next_execution_at=next_execution.isoformat(),
                        )

                    db.commit()
                    logger.info(
                        "updated_job_execution_counts",
                        job_id=request_data.job_id,
                        execution_id=request_data.execution_id,
                    )
                else:
                    logger.warning(
                        "job_update_failed_wrong_organization",
                        job_id=request_data.job_id,
                        organization_id=request_data.organization_id,
                    )
            except Exception as e:
                db.rollback()
                # Just log and continue - this is not critical
                logger.warning(
                    "failed_to_update_job_counts",
                    job_id=request_data.job_id,
                    error=str(e),
                )

        return {
            "execution_id": request_data.execution_id,
            "status": "created",
            "created_at": now.isoformat(),
        }

    except Exception as e:
        logger.error(
            "failed_to_create_job_execution_records",
            execution_id=request_data.execution_id,
            job_id=request_data.job_id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create execution records: {str(e)}"
        )


@router.get("", response_model=List[ExecutionResponse])
async def list_executions(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    status_filter: str | None = None,
    execution_type: str | None = None,
    organization: dict = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    """List all executions for the organization with optional filtering"""
    try:
        # Build SQLAlchemy query with optional participants join
        query = db.query(Execution).options(
            joinedload(Execution.participants)
        ).filter(Execution.organization_id == organization["id"])

        if status_filter:
            query = query.filter(Execution.status == status_filter.lower())
        if execution_type:
            query = query.filter(Execution.execution_type == execution_type.upper())

        results = query.order_by(desc(Execution.created_at)).offset(skip).limit(limit).all()

        if not results:
            logger.info("no_executions_found", org_id=organization["id"])
            return []

        executions = []
        for execution in results:
            try:
                # Parse participants from SQLAlchemy relationship
                participants = []
                if hasattr(execution, 'participants') and execution.participants:
                    for p in execution.participants:
                        try:
                            participants.append(ParticipantResponse(
                                id=str(p.id),
                                user_id=p.user_id,
                                user_name=p.user_name,
                                user_email=p.user_email,
                                user_avatar=p.user_avatar,
                                role=p.role,
                                joined_at=p.joined_at.isoformat() if p.joined_at else "",
                                last_active_at=p.last_active_at.isoformat() if p.last_active_at else "",
                            ))
                        except Exception as participant_error:
                            logger.warning("failed_to_parse_participant", error=str(participant_error), execution_id=str(execution.id))
                            # Skip invalid participant, continue with others

                # Sanitize JSONB fields
                usage_data = sanitize_jsonb_field(
                    execution.usage,
                    field_name=f"usage[{execution.id}]"
                )
                metadata_data = sanitize_jsonb_field(
                    execution.execution_metadata,
                    field_name=f"execution_metadata[{execution.id}]"
                )

                executions.append(
                    ExecutionResponse(
                        id=str(execution.id),
                        organization_id=execution.organization_id,
                        execution_type=execution.execution_type,
                        entity_id=str(execution.entity_id) if execution.entity_id else "",
                        entity_name=execution.entity_name,
                        prompt=execution.prompt or "",
                        system_prompt=execution.system_prompt,
                        status=execution.status,
                        response=execution.response,
                        error_message=execution.error_message,
                        usage=usage_data,
                        execution_metadata=metadata_data,
                        runner_name=execution.runner_name,
                        user_id=execution.user_id,
                        user_name=execution.user_name,
                        user_email=execution.user_email,
                        user_avatar=execution.user_avatar,
                        created_at=execution.created_at.isoformat() if execution.created_at else "",
                        started_at=execution.started_at.isoformat() if execution.started_at else None,
                        completed_at=execution.completed_at.isoformat() if execution.completed_at else None,
                        updated_at=execution.updated_at.isoformat() if execution.updated_at else "",
                        participants=participants,
                    )
                )
            except Exception as execution_error:
                logger.error("failed_to_parse_execution", error=str(execution_error), execution_id=str(execution.id))
                # Skip invalid execution, continue with others

        logger.info(
            "executions_listed_successfully",
            count=len(executions),
            org_id=organization["id"],
        )

        return executions

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "executions_list_failed",
            error=str(e),
            error_type=type(e).__name__,
            org_id=organization["id"]
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list executions: {str(e)}"
        )


class CreateJobExecutionRequest(BaseModel):
    """Request to create a job execution record"""
    execution_id: str
    job_id: str | None = None
    entity_type: str  # "agent" or "team"
    entity_id: str | None = None
    prompt: str
    trigger_type: str  # "cron", "webhook", "manual"
    trigger_metadata: dict = Field(default_factory=dict)


@router.post("/job-executions", status_code=status.HTTP_201_CREATED)
async def create_job_execution(
    request_data: CreateJobExecutionRequest,
    http_request: Request,
    organization: dict = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    """
    Create execution and job_executions records for a scheduled job.

    This endpoint is used by workers to create execution records when jobs are triggered.
    It creates both:
    1. An execution record in the executions table
    2. A job_executions junction record linking the job to the execution

    Available at both /job-executions and /create for backwards compatibility.
    """
    try:
        now = datetime.now(timezone.utc)

        # Enhanced logging for debugging stale job_id sources
        logger.info(
            "execution_request_received",
            execution_id=request_data.execution_id,
            job_id=request_data.job_id,
            trigger_type=request_data.trigger_type,
            organization_id=organization["id"],
            endpoint=http_request.url.path,
            source_headers={
                "temporal_workflow": http_request.headers.get("X-Temporal-Workflow-Id"),
                "temporal_run": http_request.headers.get("X-Temporal-Run-Id"),
            },
        )

        # Fetch entity details (name and runner_name) using SQLAlchemy
        entity_name = None
        runner_name = None

        if request_data.entity_id and request_data.entity_type:
            try:
                if request_data.entity_type == "agent":
                    entity = db.query(Agent).filter(Agent.id == request_data.entity_id).first()
                elif request_data.entity_type == "team":
                    entity = db.query(Team).filter(Team.id == request_data.entity_id).first()
                else:
                    entity = None
                if entity:
                    entity_name = entity.name
                    runner_name = getattr(entity, 'runner_name', None)
            except Exception as e:
                logger.warning(
                    "failed_to_fetch_entity_details",
                    entity_type=request_data.entity_type,
                    entity_id=request_data.entity_id,
                    error=str(e)
                )

        # Fallback: Get runner_name from active worker_queues if not found
        if not runner_name:
            try:
                queue = db.query(WorkerQueue).filter(
                    WorkerQueue.organization_id == organization["id"],
                    WorkerQueue.status == "active",
                    WorkerQueue.ephemeral == False,  # Exclude ephemeral queues
                    ~WorkerQueue.name.startswith('local-exec')  # Exclude local-exec queues
                ).first()
                if queue:
                    worker_queue_name = queue.name
                    # Extract runner_name from queue name (format: "org_id.runner_name")
                    runner_name = worker_queue_name.split(".")[-1] if "." in worker_queue_name else worker_queue_name
            except Exception as e:
                logger.warning("failed_to_fetch_runner_name_from_worker_queues", error=str(e))

        # Final fallback for runner_name
        if not runner_name:
            runner_name = "default"

        # Map trigger_type to trigger_source
        trigger_source_map = {
            "manual": "job_manual",
            "cron": "job_cron",
            "webhook": "job_webhook",
        }
        trigger_source = trigger_source_map.get(request_data.trigger_type, "job_cron")

        # Check if execution already exists (might have been created as placeholder by jobs router)
        existing = db.query(Execution).filter(
            Execution.id == request_data.execution_id,
            Execution.organization_id == organization["id"]
        ).first()

        if existing:
            # Execution exists, update it with complete information
            logger.info(
                "updating_existing_execution_record",
                execution_id=request_data.execution_id,
            )
            existing.execution_type = request_data.entity_type.upper()
            existing.entity_id = uuid_module.UUID(request_data.entity_id) if request_data.entity_id else None
            existing.entity_name = entity_name
            existing.runner_name = runner_name
            existing.trigger_source = trigger_source
            existing.trigger_metadata = {
                "job_id": request_data.job_id,
                "job_name": request_data.trigger_metadata.get("job_name"),
                "trigger_type": request_data.trigger_type,
                **request_data.trigger_metadata,
            }
            existing.user_id = request_data.trigger_metadata.get("user_id")
            existing.user_email = request_data.trigger_metadata.get("triggered_by") or request_data.trigger_metadata.get("user_email")
            existing.user_name = request_data.trigger_metadata.get("user_name")
            existing.user_avatar = request_data.trigger_metadata.get("user_avatar")
            existing.prompt = request_data.prompt
            existing.status = "pending"
            existing.usage = {}
            existing.execution_metadata = {
                "job_id": request_data.job_id,
                "job_name": request_data.trigger_metadata.get("job_name"),
                "trigger_type": request_data.trigger_type,
                "scheduled_execution": True,
                **request_data.trigger_metadata,
            }
            existing.updated_at = now
            db.commit()
        else:
            # Execution doesn't exist, create it
            logger.info(
                "creating_new_execution_record",
                execution_id=request_data.execution_id,
            )
            execution = Execution(
                id=uuid_module.UUID(request_data.execution_id),
                organization_id=organization["id"],
                execution_type=request_data.entity_type.upper(),
                entity_id=uuid_module.UUID(request_data.entity_id) if request_data.entity_id else None,
                entity_name=entity_name,
                runner_name=runner_name,
                trigger_source=trigger_source,
                trigger_metadata={
                    "job_id": request_data.job_id,
                    "job_name": request_data.trigger_metadata.get("job_name"),
                    "trigger_type": request_data.trigger_type,
                    **request_data.trigger_metadata,
                },
                user_id=request_data.trigger_metadata.get("user_id"),
                user_email=request_data.trigger_metadata.get("triggered_by") or request_data.trigger_metadata.get("user_email"),
                user_name=request_data.trigger_metadata.get("user_name"),
                user_avatar=request_data.trigger_metadata.get("user_avatar"),
                prompt=request_data.prompt,
                status="pending",
                usage={},
                execution_metadata={
                    "job_id": request_data.job_id,
                    "job_name": request_data.trigger_metadata.get("job_name"),
                    "trigger_type": request_data.trigger_type,
                    "scheduled_execution": True,
                    **request_data.trigger_metadata,
                },
                created_at=now,
                updated_at=now,
            )
            db.add(execution)
            db.commit()

        # Create job_executions junction record if job_id is provided
        if request_data.job_id:
            # VALIDATION: Ensure job exists and belongs to organization
            job = await validate_job_exists(
                db=db,
                job_id=request_data.job_id,
                organization_id=organization["id"],
                logger_context={
                    "execution_id": request_data.execution_id,
                    "trigger_type": request_data.trigger_type,
                    "source": "create_job_execution",
                }
            )

            logger.info(
                "checking_job_execution_junction",
                job_id=request_data.job_id,
                job_name=job.get("name"),
                execution_id=request_data.execution_id,
            )

            # Check if junction record already exists (with org_id for security)
            existing_junction = db.query(JobExecution).filter(
                JobExecution.job_id == request_data.job_id,
                JobExecution.execution_id == request_data.execution_id,
                JobExecution.organization_id == organization["id"]
            ).first()

            if not existing_junction:
                # Only create if it doesn't exist
                try:
                    job_execution = JobExecution(
                        id=str(uuid_module.uuid4()),
                        job_id=request_data.job_id,
                        execution_id=uuid_module.UUID(request_data.execution_id),
                        organization_id=organization["id"],
                        trigger_type=request_data.trigger_type,
                        trigger_metadata=request_data.trigger_metadata,
                        execution_status="pending",
                        created_at=now,
                    )
                    db.add(job_execution)
                    db.commit()
                    logger.info(
                        "job_execution_junction_created",
                        job_id=request_data.job_id,
                        execution_id=request_data.execution_id,
                    )
                except Exception as insert_error:
                    db.rollback()
                    logger.error(
                        "job_execution_junction_insert_failed",
                        job_id=request_data.job_id,
                        execution_id=request_data.execution_id,
                        error=str(insert_error),
                    )
                    # Continue - don't fail the whole request
            else:
                logger.info(
                    "job_execution_junction_already_exists",
                    job_id=request_data.job_id,
                    execution_id=request_data.execution_id,
                )

        logger.info(
            "created_job_execution_records",
            execution_id=request_data.execution_id,
            job_id=request_data.job_id,
            trigger_type=request_data.trigger_type,
        )

        return {
            "execution_id": request_data.execution_id,
            "status": "created",
            "message": "Job execution records created successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "failed_to_create_job_execution",
            error=str(e),
            execution_id=request_data.execution_id,
            job_id=request_data.job_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job execution: {str(e)}"
        )


class UpdateJobExecutionStatusRequest(BaseModel):
    """Request to update job execution status"""
    status: str
    duration_ms: int | None = None
    error_message: str | None = None


@router.post("/{execution_id}/job/{job_id}/status", status_code=status.HTTP_202_ACCEPTED)
async def update_job_execution_status(
    execution_id: str,
    job_id: str,
    request: UpdateJobExecutionStatusRequest,
    organization: dict = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    """
    Update job execution status after completion.

    This endpoint is called by workers to update the job_executions junction record
    when a job execution completes or fails.
    """
    try:
        now = datetime.now(timezone.utc)

        # Update job_executions record using SQLAlchemy
        job_execution = db.query(JobExecution).filter(
            JobExecution.job_id == job_id,
            JobExecution.execution_id == execution_id,
            JobExecution.organization_id == organization["id"]
        ).first()

        if not job_execution:
            logger.warning(
                "job_execution_not_found_for_status_update",
                job_id=job_id,
                execution_id=execution_id,
            )
            # Don't fail - return success anyway
            return {
                "job_id": job_id,
                "execution_id": execution_id,
                "status": "not_found"
            }

        job_execution.execution_status = request.status
        job_execution.updated_at = now

        if request.duration_ms is not None:
            job_execution.execution_duration_ms = request.duration_ms

        db.commit()

        # Update job statistics based on status using SQLAlchemy
        job = db.query(Job).filter(
            Job.id == job_id,
            Job.organization_id == organization["id"]
        ).first()

        if job:
            if request.status == "completed":
                job.successful_executions = (job.successful_executions or 0) + 1
            elif request.status == "failed":
                job.failed_executions = (job.failed_executions or 0) + 1
            db.commit()

        logger.info(
            "updated_job_execution_status",
            job_id=job_id,
            execution_id=execution_id,
            status=request.status,
        )

        return {
            "job_id": job_id,
            "execution_id": execution_id,
            "status": "updated"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "failed_to_update_job_execution_status",
            error=str(e),
            job_id=job_id,
            execution_id=execution_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update job execution status: {str(e)}"
        )


@router.get("/{execution_id}", response_model=ExecutionResponse)
async def get_execution(
    execution_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    """Get a specific execution by ID"""
    try:
        execution = db.query(Execution).filter(
            Execution.id == uuid_module.UUID(execution_id),
            Execution.organization_id == organization["id"]
        ).first()

        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")

        # Sanitize JSONB fields
        usage_data = sanitize_jsonb_field(
            execution.usage,
            field_name=f"usage[{execution_id}]"
        )
        metadata_data = sanitize_jsonb_field(
            execution.execution_metadata,
            field_name=f"execution_metadata[{execution_id}]"
        )

        return ExecutionResponse(
            id=str(execution.id),
            organization_id=execution.organization_id,
            execution_type=execution.execution_type,
            entity_id=str(execution.entity_id),
            entity_name=execution.entity_name,
            prompt=execution.prompt or "",
            system_prompt=execution.system_prompt,
            status=execution.status,
            response=execution.response,
            error_message=execution.error_message,
            usage=usage_data,
            execution_metadata=metadata_data,
            runner_name=execution.runner_name,
            user_id=execution.user_id,
            user_name=execution.user_name,
            user_email=execution.user_email,
            user_avatar=execution.user_avatar,
            created_at=execution.created_at.isoformat() if execution.created_at else None,
            started_at=execution.started_at.isoformat() if execution.started_at else None,
            completed_at=execution.completed_at.isoformat() if execution.completed_at else None,
            updated_at=execution.updated_at.isoformat() if execution.updated_at else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("execution_get_failed", error=str(e), execution_id=execution_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get execution: {str(e)}"
        )


@router.delete("/{execution_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_execution(
    execution_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    """Delete an execution"""
    try:
        execution = db.query(Execution).filter(
            Execution.id == uuid_module.UUID(execution_id),
            Execution.organization_id == organization["id"]
        ).first()

        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")

        db.delete(execution)
        db.commit()

        logger.info("execution_deleted", execution_id=execution_id, org_id=organization["id"])

        return None

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("execution_delete_failed", error=str(e), execution_id=execution_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete execution: {str(e)}"
        )


class ExecutionUpdate(BaseModel):
    """Update execution fields - used by workers to update execution status"""
    status: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    response: str | None = None
    error_message: str | None = None
    usage: dict | None = None
    execution_metadata: dict | None = None


@router.patch("/{execution_id}", response_model=ExecutionResponse)
async def update_execution(
    execution_id: str,
    execution_update: ExecutionUpdate,
    request: Request,
    organization: dict = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    """
    Update execution status and results.

    This endpoint is primarily used by workers to update execution status,
    results, usage metrics, and metadata during execution.
    """
    try:
        execution = db.query(Execution).filter(
            Execution.id == uuid_module.UUID(execution_id),
            Execution.organization_id == organization["id"]
        ).first()

        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")

        # Track fields that were updated
        updated_fields = []

        if execution_update.status is not None:
            execution.status = execution_update.status.lower()  # Normalize to lowercase
            updated_fields.append("status")

        if execution_update.started_at is not None:
            execution.started_at = datetime.fromisoformat(execution_update.started_at.replace('Z', '+00:00'))
            updated_fields.append("started_at")

        if execution_update.completed_at is not None:
            execution.completed_at = datetime.fromisoformat(execution_update.completed_at.replace('Z', '+00:00'))
            updated_fields.append("completed_at")

        if execution_update.response is not None:
            execution.response = execution_update.response
            updated_fields.append("response")

        if execution_update.error_message is not None:
            execution.error_message = execution_update.error_message
            updated_fields.append("error_message")

        if execution_update.usage is not None:
            execution.usage = execution_update.usage
            updated_fields.append("usage")

        if execution_update.execution_metadata is not None:
            execution.execution_metadata = execution_update.execution_metadata
            updated_fields.append("execution_metadata")

        # updated_at will be automatically set by onupdate
        updated_fields.append("updated_at")

        db.commit()
        db.refresh(execution)

        logger.info(
            "execution_updated",
            execution_id=execution_id,
            org_id=organization["id"],
            fields_updated=updated_fields,
        )

        # Sanitize JSONB fields before returning
        usage_data = sanitize_jsonb_field(
            execution.usage,
            field_name=f"usage[{execution_id}]"
        )
        metadata_data = sanitize_jsonb_field(
            execution.execution_metadata,
            field_name=f"execution_metadata[{execution_id}]"
        )

        return ExecutionResponse(
            id=str(execution.id),
            organization_id=execution.organization_id,
            execution_type=execution.execution_type,
            entity_id=str(execution.entity_id),
            entity_name=execution.entity_name,
            prompt=execution.prompt or "",
            system_prompt=execution.system_prompt,
            status=execution.status,
            response=execution.response,
            error_message=execution.error_message,
            usage=usage_data,
            execution_metadata=metadata_data,
            runner_name=execution.runner_name,
            user_id=execution.user_id,
            user_name=execution.user_name,
            user_email=execution.user_email,
            user_avatar=execution.user_avatar,
            created_at=execution.created_at.isoformat() if execution.created_at else None,
            started_at=execution.started_at.isoformat() if execution.started_at else None,
            completed_at=execution.completed_at.isoformat() if execution.completed_at else None,
            updated_at=execution.updated_at.isoformat() if execution.updated_at else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("execution_update_failed", error=str(e), execution_id=execution_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update execution: {str(e)}"
        )


class SendMessageRequest(BaseModel):
    """Request to send a message to a running execution"""
    message: str
    role: str = "user"  # user, system, etc.


@router.post("/{execution_id}/message", status_code=status.HTTP_202_ACCEPTED)
async def send_message_to_execution(
    execution_id: str,
    request_body: SendMessageRequest,
    request: Request,
    organization: dict = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    """
    Send a followup message to a running execution using Temporal signals.

    This sends a signal to the Temporal workflow, adding the message to the conversation.
    The workflow will process the message and respond accordingly.
    """
    try:
        # Get Temporal client
        temporal_client = await get_temporal_client()

        # Verify the execution belongs to this organization and get execution type
        execution = db.query(Execution).filter(
            Execution.id == uuid_module.UUID(execution_id),
            Execution.organization_id == organization["id"]
        ).first()

        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")

        # Construct workflow ID based on execution type
        execution_type = execution.execution_type or "AGENT"
        if execution_type == "TEAM":
            workflow_id = f"team-execution-{execution_id}"
        else:
            workflow_id = f"agent-execution-{execution_id}"

        workflow_handle = temporal_client.get_workflow_handle(workflow_id)

        # Import ChatMessage from workflow
        from control_plane_api.app.workflows.agent_execution import ChatMessage
        from datetime import datetime, timezone
        import time

        # Generate message_id FIRST so we can use it in both ChatMessage and Redis event
        message_id = f"{execution_id}_{int(time.time() * 1000000)}"

        # Create the message with user attribution from JWT token AND message_id
        message = ChatMessage(
            role=request_body.role,
            content=request_body.message,
            timestamp=datetime.now(timezone.utc).isoformat(),
            message_id=message_id,  # CRITICAL: Pass message_id to workflow for consistent deduplication
            user_id=organization.get("user_id"),
            user_name=organization.get("user_name"),
            user_email=organization.get("user_email"),
            user_avatar=organization.get("user_avatar"),  # Now available from JWT via auth middleware
        )

        # CRITICAL: Publish to Redis for immediate SSE streaming
        # The workflow will save to database - we just need instant UI update
        redis_client = get_redis_client()
        if redis_client:
            try:
                event_data = {
                    "event_type": "message",
                    "data": {
                        "role": message.role,
                        "content": message.content,
                        "timestamp": message.timestamp,
                        "message_id": message_id,
                        "user_id": message.user_id,
                        "user_name": message.user_name,
                        "user_email": message.user_email,
                        "user_avatar": message.user_avatar,
                    },
                    "timestamp": message.timestamp,
                    "execution_id": execution_id,
                }

                redis_key = f"execution:{execution_id}:events"
                await redis_client.lpush(redis_key, json.dumps(event_data))
                await redis_client.ltrim(redis_key, 0, 999)
                await redis_client.expire(redis_key, 3600)

                logger.info(
                    "user_message_published_to_redis",
                    execution_id=execution_id,
                    message_id=message_id,
                )
            except Exception as redis_error:
                logger.warning(
                    "failed_to_publish_user_message_to_redis",
                    error=str(redis_error),
                    execution_id=execution_id,
                )
                # Continue - not critical

        # Send signal to workflow
        await workflow_handle.signal(AgentExecutionWorkflow.add_message, message)

        # Add user as participant if not already added (multiplayer support)
        user_id = organization.get("user_id")
        if user_id:
            try:
                # Check if participant already exists
                existing = db.query(ExecutionParticipant).filter(
                    ExecutionParticipant.execution_id == uuid_module.UUID(execution_id),
                    ExecutionParticipant.user_id == user_id
                ).first()

                if not existing:
                    # Add as new participant (collaborator role)
                    import uuid
                    new_participant = ExecutionParticipant(
                        id=uuid.uuid4(),
                        execution_id=uuid_module.UUID(execution_id),
                        organization_id=organization["id"],
                        user_id=user_id,
                        user_name=organization.get("user_name"),
                        user_email=organization.get("user_email"),
                        user_avatar=organization.get("user_avatar"),
                        role="collaborator",
                    )
                    db.add(new_participant)
                    db.commit()
                    logger.info(
                        "participant_added",
                        execution_id=execution_id,
                        user_id=user_id,
                    )
                else:
                    # Update last_active_at for existing participant
                    from datetime import timezone
                    existing.last_active_at = datetime.now(timezone.utc)
                    db.commit()
            except Exception as participant_error:
                db.rollback()
                logger.warning(
                    "failed_to_add_participant",
                    error=str(participant_error),
                    execution_id=execution_id,
                )
                # Don't fail the whole request if participant tracking fails

        logger.info(
            "message_sent_to_execution",
            execution_id=execution_id,
            org_id=organization["id"],
            role=request_body.role,
        )

        return {
            "success": True,
            "execution_id": execution_id,
            "message": "Message sent to workflow",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "send_message_failed",
            error=str(e),
            execution_id=execution_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.post("/{execution_id}/pause")
async def pause_execution(
    execution_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    """
    Pause an active execution by sending a signal to the Temporal workflow.

    This is triggered when the user clicks the PAUSE button in the UI.
    The workflow will stop processing but remain active and can be resumed.
    """
    try:
        logger.info(
            "pause_execution_requested",
            execution_id=execution_id,
            org_id=organization["id"]
        )

        # Get execution from database
        execution = db.query(Execution).filter(
            Execution.id == uuid_module.UUID(execution_id),
            Execution.organization_id == organization["id"]
        ).first()

        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Execution not found"
            )

        current_status = execution.status

        # Check if execution can be paused
        if current_status not in ["running", "waiting_for_input"]:
            logger.warning(
                "pause_execution_invalid_status",
                execution_id=execution_id,
                status=current_status
            )
            return {
                "success": False,
                "error": f"Execution cannot be paused (status: {current_status})",
                "execution_id": execution_id,
                "status": current_status,
            }

        # Get Temporal client
        temporal_client = await get_temporal_client()

        # Determine workflow ID based on execution type
        execution_type = execution.execution_type or "AGENT"
        workflow_id = f"team-execution-{execution_id}" if execution_type == "TEAM" else f"agent-execution-{execution_id}"

        workflow_handle = temporal_client.get_workflow_handle(workflow_id)

        # Send pause signal to workflow
        await workflow_handle.signal(AgentExecutionWorkflow.pause_execution)

        # Update execution status to paused
        execution.status = "paused"
        db.commit()

        # Emit system message to Redis for UI display
        redis_client = get_redis_client()
        if redis_client:
            try:
                import time
                user_name = organization.get("user_name", "User")
                current_timestamp = datetime.now(timezone.utc).isoformat()
                message_id = f"{execution_id}_pause_{int(time.time() * 1000000)}"

                # Create message event - format matches what streaming endpoint expects
                pause_message_event = {
                    "event_type": "message",
                    "data": {
                        "role": "system",
                        "content": f"⏸️ Execution paused by {user_name}",
                        "timestamp": current_timestamp,
                        "message_id": message_id,
                    },
                    "timestamp": current_timestamp,
                    "execution_id": execution_id,
                }

                redis_key = f"execution:{execution_id}:events"
                await redis_client.lpush(redis_key, json.dumps(pause_message_event))
                await redis_client.ltrim(redis_key, 0, 999)
                await redis_client.expire(redis_key, 3600)

                # Also update status event
                status_event = {
                    "event_type": "status",
                    "data": {"status": "paused", "execution_id": execution_id},
                    "timestamp": current_timestamp,
                    "execution_id": execution_id,
                }
                await redis_client.lpush(redis_key, json.dumps(status_event))

                logger.debug("pause_event_published_to_redis", execution_id=execution_id)
            except Exception as redis_error:
                logger.warning("failed_to_publish_pause_event", error=str(redis_error), execution_id=execution_id)

        logger.info(
            "execution_paused_successfully",
            execution_id=execution_id,
            workflow_id=workflow_id
        )

        return {
            "success": True,
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "message": "Execution paused successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(
            "pause_execution_error",
            execution_id=execution_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pause execution: {str(e)}"
        )


@router.post("/{execution_id}/resume")
async def resume_execution(
    execution_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    """
    Resume a paused execution by sending a signal to the Temporal workflow.

    This is triggered when the user clicks the RESUME button in the UI.
    The workflow will continue processing from where it was paused.
    """
    try:
        logger.info(
            "resume_execution_requested",
            execution_id=execution_id,
            org_id=organization["id"]
        )

        # Get execution from database
        execution = db.query(Execution).filter(
            Execution.id == uuid_module.UUID(execution_id),
            Execution.organization_id == organization["id"]
        ).first()

        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Execution not found"
            )

        current_status = execution.status

        # Check if execution is paused
        if current_status != "paused":
            logger.warning(
                "resume_execution_not_paused",
                execution_id=execution_id,
                status=current_status
            )
            return {
                "success": False,
                "error": f"Execution is not paused (status: {current_status})",
                "execution_id": execution_id,
                "status": current_status,
            }

        # Get Temporal client
        temporal_client = await get_temporal_client()

        # Determine workflow ID based on execution type
        execution_type = execution.execution_type or "AGENT"
        workflow_id = f"team-execution-{execution_id}" if execution_type == "TEAM" else f"agent-execution-{execution_id}"

        workflow_handle = temporal_client.get_workflow_handle(workflow_id)

        # Send resume signal to workflow
        await workflow_handle.signal(AgentExecutionWorkflow.resume_execution)

        # Update execution status back to running/waiting
        # The workflow will determine the correct status
        execution.status = "running"
        db.commit()

        # Emit system message to Redis for UI display
        redis_client = get_redis_client()
        if redis_client:
            try:
                import time
                user_name = organization.get("user_name", "User")
                current_timestamp = datetime.now(timezone.utc).isoformat()
                message_id = f"{execution_id}_resume_{int(time.time() * 1000000)}"

                # Create message event - format matches what streaming endpoint expects
                resume_message_event = {
                    "event_type": "message",
                    "data": {
                        "role": "system",
                        "content": f"▶️ Execution resumed by {user_name}",
                        "timestamp": current_timestamp,
                        "message_id": message_id,
                    },
                    "timestamp": current_timestamp,
                    "execution_id": execution_id,
                }

                redis_key = f"execution:{execution_id}:events"
                await redis_client.lpush(redis_key, json.dumps(resume_message_event))
                await redis_client.ltrim(redis_key, 0, 999)
                await redis_client.expire(redis_key, 3600)

                # Also update status event
                status_event = {
                    "event_type": "status",
                    "data": {"status": "running", "execution_id": execution_id},
                    "timestamp": current_timestamp,
                    "execution_id": execution_id,
                }
                await redis_client.lpush(redis_key, json.dumps(status_event))

                logger.debug("resume_event_published_to_redis", execution_id=execution_id)
            except Exception as redis_error:
                logger.warning("failed_to_publish_resume_event", error=str(redis_error), execution_id=execution_id)

        logger.info(
            "execution_resumed_successfully",
            execution_id=execution_id,
            workflow_id=workflow_id
        )

        return {
            "success": True,
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "message": "Execution resumed successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(
            "resume_execution_error",
            execution_id=execution_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resume execution: {str(e)}"
        )


@router.post("/{execution_id}/cancel")
async def cancel_execution(
    execution_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    """
    Cancel an active execution by calling Temporal's workflow cancellation.

    This is triggered when the user clicks the STOP button in the UI.
    It uses Temporal's built-in cancellation which is fast and returns immediately.
    """
    try:
        from temporalio.client import WorkflowHandle

        logger.info(
            "cancel_execution_requested",
            execution_id=execution_id,
            org_id=organization["id"]
        )

        # Get execution from database
        execution = db.query(Execution).filter(
            Execution.id == uuid_module.UUID(execution_id),
            Execution.organization_id == organization["id"]
        ).first()

        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Execution not found"
            )

        current_status = execution.status

        # Check if execution is still running
        if current_status not in ["running", "waiting_for_input"]:
            logger.warning(
                "cancel_execution_not_running",
                execution_id=execution_id,
                status=current_status
            )
            return {
                "success": False,
                "error": f"Execution is not running (status: {current_status})",
                "execution_id": execution_id,
                "status": current_status,
            }

        # Get Temporal client
        temporal_client = await get_temporal_client()

        # Determine workflow ID based on execution type
        execution_type = execution.execution_type or "AGENT"
        workflow_id = f"team-execution-{execution_id}" if execution_type == "TEAM" else f"agent-execution-{execution_id}"

        workflow_handle: WorkflowHandle = temporal_client.get_workflow_handle(
            workflow_id=workflow_id
        )

        # Use Temporal's built-in workflow cancellation
        # This is fast and returns immediately
        try:
            # Send cancel signal to the workflow
            # This returns immediately - it doesn't wait for the workflow to finish
            await workflow_handle.cancel()

            # Update execution status to cancelled
            execution.status = "cancelled"
            execution.completed_at = datetime.utcnow()
            execution.error_message = "Cancelled by user"
            db.commit()

            # Emit system message to Redis for UI display
            redis_client = get_redis_client()
            if redis_client:
                try:
                    import time
                    user_name = organization.get("user_name", "User")
                    current_timestamp = datetime.now(timezone.utc).isoformat()
                    message_id = f"{execution_id}_cancel_{int(time.time() * 1000000)}"

                    # Create message event - format matches what streaming endpoint expects
                    cancel_message_event = {
                        "event_type": "message",
                        "data": {
                            "role": "system",
                            "content": f"🛑 Execution stopped by {user_name}",
                            "timestamp": current_timestamp,
                            "message_id": message_id,
                        },
                        "timestamp": current_timestamp,
                        "execution_id": execution_id,
                    }

                    redis_key = f"execution:{execution_id}:events"
                    await redis_client.lpush(redis_key, json.dumps(cancel_message_event))
                    await redis_client.ltrim(redis_key, 0, 999)
                    await redis_client.expire(redis_key, 3600)

                    # Also update status event
                    status_event = {
                        "event_type": "status",
                        "data": {"status": "cancelled", "execution_id": execution_id},
                        "timestamp": current_timestamp,
                        "execution_id": execution_id,
                    }
                    await redis_client.lpush(redis_key, json.dumps(status_event))

                    logger.debug("cancel_event_published_to_redis", execution_id=execution_id)
                except Exception as redis_error:
                    logger.warning("failed_to_publish_cancel_event", error=str(redis_error), execution_id=execution_id)

            logger.info(
                "execution_cancelled_successfully",
                execution_id=execution_id,
                workflow_id=workflow_id
            )

            return {
                "success": True,
                "execution_id": execution_id,
                "workflow_id": workflow_id,
                "message": "Execution cancelled successfully",
            }

        except Exception as cancel_error:
            logger.error(
                "cancel_workflow_error",
                execution_id=execution_id,
                error=str(cancel_error)
            )

            # Mark as cancelled in database anyway (user intent matters)
            execution.status = "cancelled"
            execution.completed_at = datetime.utcnow()
            execution.error_message = f"Cancelled: {str(cancel_error)}"
            db.commit()

            return {
                "success": True,  # User intent succeeded
                "execution_id": execution_id,
                "message": "Execution marked as cancelled",
                "warning": str(cancel_error),
            }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(
            "cancel_execution_error",
            execution_id=execution_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel execution: {str(e)}"
        )


class CancelWorkflowRequest(BaseModel):
    """Request to cancel a specific workflow"""
    workflow_message_id: str


@router.post("/{execution_id}/cancel_workflow")
async def cancel_workflow(
    execution_id: str,
    cancel_request: CancelWorkflowRequest,
    request: Request,
    organization: dict = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    """
    Cancel a specific workflow tool call within an execution.

    This cancels only the workflow, allowing the agent to continue running
    and respond to the user about the cancellation. This is different from
    /cancel which stops the entire execution.

    Args:
        execution_id: The agent execution ID
        workflow_message_id: The unique workflow message ID to cancel
    """
    workflow_message_id = None  # Initialize to avoid UnboundLocalError
    try:
        from control_plane_api.app.services.workflow_cancellation_manager import workflow_cancellation_manager

        workflow_message_id = cancel_request.workflow_message_id

        logger.info(
            "cancel_workflow_requested",
            execution_id=execution_id,
            workflow_message_id=workflow_message_id,
            org_id=organization["id"]
        )

        # Get execution from database to verify it exists and is running
        execution = db.query(Execution).filter(
            Execution.id == uuid_module.UUID(execution_id),
            Execution.organization_id == organization["id"]
        ).first()

        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Execution not found"
            )

        current_status = execution.status

        # Check if execution is still running
        if current_status not in ["running", "waiting_for_input"]:
            logger.warning(
                "cancel_workflow_execution_not_running",
                execution_id=execution_id,
                status=current_status
            )
            return {
                "success": False,
                "error": f"Execution is not running (status: {current_status})",
                "execution_id": execution_id,
                "workflow_message_id": workflow_message_id,
                "status": current_status,
            }

        # Request cancellation via the workflow cancellation manager
        # The workflow executor will check this flag and stop gracefully
        workflow_cancellation_manager.request_cancellation(execution_id, workflow_message_id)

        logger.info(
            "workflow_cancellation_flag_set",
            execution_id=execution_id,
            workflow_message_id=workflow_message_id
        )

        # Publish a workflow_cancelled event to update the UI immediately
        redis_client = get_redis_client()
        if redis_client:
            try:
                import time
                current_timestamp = datetime.now(timezone.utc).isoformat()

                # Create workflow_cancelled event for immediate UI feedback
                cancel_event = {
                    "event_type": "workflow_cancelled",
                    "data": {
                        "workflow_name": "Workflow",  # Will be updated by executor with actual name
                        "status": "cancelled",
                        "finished_at": current_timestamp,
                        "message": "Workflow cancellation requested",
                        "source": "workflow",
                        "message_id": workflow_message_id,
                    },
                    "timestamp": current_timestamp,
                }

                redis_key = f"execution:{execution_id}:events"
                redis_client.rpush(redis_key, json.dumps(cancel_event))
                redis_client.expire(redis_key, 3600)  # 1 hour TTL

                logger.info(
                    "workflow_cancel_event_published",
                    execution_id=execution_id,
                    workflow_message_id=workflow_message_id
                )
            except Exception as e:
                logger.warning(
                    "failed_to_publish_workflow_cancel_event",
                    error=str(e),
                    execution_id=execution_id
                )

        return {
            "success": True,
            "execution_id": execution_id,
            "workflow_message_id": workflow_message_id,
            "message": "Workflow cancellation requested. The workflow will stop at the next check point.",
            "cancelled_at": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "cancel_workflow_error",
            execution_id=execution_id,
            workflow_message_id=workflow_message_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel workflow: {str(e)}"
        )


@router.get("/{execution_id}/session")
async def get_session_history(
    execution_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    """
    Retrieve session history with Redis caching for hot loading.

    Workers GET session messages before each run to restore conversation context.

    Performance strategy:
    1. Check Redis cache first (hot path - milliseconds)
    2. Fall back to database if not cached (cold path - ~50ms)
    3. Cache the result in Redis for next access
    """
    import json
    try:
        session_id = execution_id
        redis_key = f"session:{session_id}"

        # Try Redis first for hot loading
        redis_client = get_redis_client()
        if redis_client:
            try:
                cached_session = await redis_client.get(redis_key)
                if cached_session:
                    session_data = json.loads(cached_session)

                    # CRITICAL: Deduplicate and sort messages to ensure consistency
                    # Apply to cached data as well to guarantee no duplicates
                    if "messages" in session_data and session_data["messages"]:
                        # Two-level deduplication: message_id + content signature
                        seen_message_ids = {}
                        seen_content_sigs = {}  # Track content signatures for assistant messages
                        deduplicated_messages = []

                        for msg in session_data["messages"]:
                            msg_id = msg.get("message_id")

                            # Level 1: Deduplicate by message_id
                            if msg_id and msg_id in seen_message_ids:
                                continue
                            if msg_id:
                                seen_message_ids[msg_id] = True

                            # Level 2: Deduplicate by content signature (assistant messages only)
                            if msg.get("role") == "assistant":
                                content = msg.get("content", "")
                                timestamp = msg.get("timestamp", "")
                                content_normalized = content.strip().lower()[:200]

                                if content_normalized and content_normalized in seen_content_sigs:
                                    prev_msg = seen_content_sigs[content_normalized]
                                    prev_timestamp = prev_msg.get("timestamp", "")

                                    # Check timestamp proximity (within 5 seconds)
                                    try:
                                        from datetime import datetime
                                        t1 = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                        t2 = datetime.fromisoformat(prev_timestamp.replace('Z', '+00:00'))
                                        diff = abs((t1 - t2).total_seconds())

                                        if diff <= 5:
                                            logger.info(
                                                "duplicate_content_filtered_redis_cache",
                                                message_id=msg_id,
                                                prev_message_id=prev_msg.get("message_id"),
                                                content_preview=content[:50]
                                            )
                                            continue  # Skip duplicate content
                                    except:
                                        pass  # If can't parse timestamps, don't skip

                                if content_normalized:
                                    seen_content_sigs[content_normalized] = msg

                            deduplicated_messages.append(msg)

                        # Sort by timestamp (use far future date for missing timestamps to put them last)
                        session_data["messages"] = sorted(
                            deduplicated_messages,
                            key=lambda msg: msg.get("timestamp", "9999-12-31T23:59:59Z")
                        )
                        session_data["message_count"] = len(session_data["messages"])

                    logger.info(
                        "session_cache_hit",
                        execution_id=execution_id,
                        message_count=session_data.get("message_count", 0)
                    )
                    return session_data
            except Exception as redis_error:
                logger.warning("session_cache_error", error=str(redis_error))
                # Continue to DB fallback

        # Redis miss or unavailable - load from database
        session_record = db.query(SessionModel).filter(
            SessionModel.execution_id == execution_id,
            SessionModel.organization_id == organization["id"]
        ).first()

        if not session_record:
            raise HTTPException(status_code=404, detail="Session not found")

        messages = session_record.messages or []

        # CRITICAL: Deduplicate messages by message_id AND content to prevent duplicates
        # This handles any duplicates that may have been persisted in the database
        # Two-level deduplication: message_id + content signature
        seen_message_ids = {}
        seen_content_sigs = {}  # Track content signatures for assistant messages
        deduplicated_messages = []

        for msg in messages:
            msg_id = msg.get("message_id")

            # Level 1: Deduplicate by message_id
            if msg_id and msg_id in seen_message_ids:
                # Skip duplicate message
                continue
            if msg_id:
                seen_message_ids[msg_id] = True

            # Level 2: Deduplicate by content signature (assistant messages only)
            if msg.get("role") == "assistant":
                content = msg.get("content", "")
                timestamp = msg.get("timestamp", "")
                content_normalized = content.strip().lower()[:200]

                if content_normalized and content_normalized in seen_content_sigs:
                    prev_msg = seen_content_sigs[content_normalized]
                    prev_timestamp = prev_msg.get("timestamp", "")

                    # Check timestamp proximity (within 5 seconds)
                    try:
                        from datetime import datetime
                        t1 = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        t2 = datetime.fromisoformat(prev_timestamp.replace('Z', '+00:00'))
                        diff = abs((t1 - t2).total_seconds())

                        if diff <= 5:
                            logger.info(
                                "duplicate_content_filtered_database",
                                message_id=msg_id,
                                prev_message_id=prev_msg.get("message_id"),
                                content_preview=content[:50]
                            )
                            continue  # Skip duplicate content
                    except:
                        pass  # If can't parse timestamps, don't skip

                if content_normalized:
                    seen_content_sigs[content_normalized] = msg

            deduplicated_messages.append(msg)

        # CRITICAL: Sort messages by timestamp to ensure chronological order
        # This guarantees consistent ordering regardless of how they're stored in JSONB
        # Use far future date for missing timestamps to put them last
        messages_sorted = sorted(deduplicated_messages, key=lambda msg: msg.get("timestamp", "9999-12-31T23:59:59Z"))

        session_data = {
            "session_id": session_record.session_id or execution_id,
            "execution_id": execution_id,
            "messages": messages_sorted,
            "message_count": len(messages_sorted),
            "metadata": session_record.metadata_ or {},
        }

        # Cache in Redis for next access (TTL: 1 hour)
        if redis_client:
            try:
                await redis_client.setex(
                    redis_key,
                    3600,  # 1 hour TTL
                    json.dumps(session_data)
                )
                logger.info(
                    "session_cached",
                    execution_id=execution_id,
                    message_count=len(messages)
                )
            except Exception as cache_error:
                logger.warning("session_cache_write_error", error=str(cache_error))

        logger.info(
            "session_history_retrieved_from_database",
            execution_id=execution_id,
            session_id=session_record.session_id,
            message_count=len(messages)
        )

        return session_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "failed_to_retrieve_session_history",
            execution_id=execution_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve session history: {str(e)}"
        )


@router.post("/{execution_id}/session", status_code=status.HTTP_201_CREATED)
async def persist_session_history(
    execution_id: str,
    session_data: dict,
    request: Request,
    organization: dict = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    """
    Persist session history from worker to Control Plane database.

    Worker POSTs session messages after each run completion.
    This ensures history is available even when worker is offline.

    Sessions are stored in database for fast loading by the UI streaming endpoint.
    """
    try:
        session_id = session_data.get("session_id", execution_id)
        user_id = session_data.get("user_id")
        messages = session_data.get("messages", [])
        metadata = session_data.get("metadata", {})

        logger.info(
            "persisting_session_history",
            execution_id=execution_id,
            session_id=session_id,
            user_id=user_id,
            message_count=len(messages),
            org_id=organization["id"],
        )

        # CRITICAL: Ensure all messages have message_id before persisting
        # Without message_id, messages cannot be properly sent via SSE stream
        messages_with_ids = []
        for msg in messages:
            if not msg.get("message_id"):
                # Generate stable message_id from timestamp and role
                timestamp_str = msg.get("timestamp")
                role = msg.get("role", "unknown")

                if timestamp_str:
                    try:
                        timestamp_micros = int(datetime.fromisoformat(timestamp_str.replace('Z', '+00:00')).timestamp() * 1000000)
                    except Exception:
                        timestamp_micros = int(datetime.utcnow().timestamp() * 1000000)
                else:
                    timestamp_micros = int(datetime.utcnow().timestamp() * 1000000)

                msg["message_id"] = f"{execution_id}_{role}_{timestamp_micros}"
                logger.info(
                    "generated_missing_message_id",
                    execution_id=execution_id,
                    role=role,
                    message_id=msg["message_id"]
                )

            messages_with_ids.append(msg)

        # DEFENSIVE: Deduplicate messages at API level (defense-in-depth)
        # This prevents duplicates even if worker didn't deduplicate properly
        # Two-level deduplication: message_id + content signature
        original_count = len(messages_with_ids)
        seen_ids = set()
        seen_content_sigs = {}  # Track content signatures for assistant messages
        deduplicated_messages = []
        duplicates_by_id = 0
        duplicates_by_content = 0

        for msg in messages_with_ids:
            msg_id = msg.get("message_id")

            # Level 1: Deduplicate by message_id
            if msg_id and msg_id in seen_ids:
                logger.debug(
                    "api_deduplication_skipped_duplicate_id",
                    execution_id=execution_id,
                    message_id=msg_id,
                    role=msg.get("role")
                )
                duplicates_by_id += 1
                continue

            if msg_id:
                seen_ids.add(msg_id)

            # Level 2: Deduplicate by content signature (assistant messages only)
            if msg.get("role") == "assistant":
                content = msg.get("content", "")
                timestamp = msg.get("timestamp", "")
                content_normalized = content.strip().lower()[:200]

                if content_normalized and content_normalized in seen_content_sigs:
                    prev_msg = seen_content_sigs[content_normalized]
                    prev_timestamp = prev_msg.get("timestamp", "")

                    # Check timestamp proximity (within 5 seconds)
                    try:
                        t1 = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        t2 = datetime.fromisoformat(prev_timestamp.replace('Z', '+00:00'))
                        diff = abs((t1 - t2).total_seconds())

                        if diff <= 5:
                            logger.info(
                                "api_deduplication_skipped_duplicate_content",
                                execution_id=execution_id,
                                message_id=msg_id,
                                prev_message_id=prev_msg.get("message_id"),
                                content_preview=content[:50]
                            )
                            duplicates_by_content += 1
                            continue  # Skip duplicate content
                    except:
                        pass  # If can't parse timestamps, don't skip

                if content_normalized:
                    seen_content_sigs[content_normalized] = msg

            deduplicated_messages.append(msg)

        messages_with_ids = deduplicated_messages

        if len(messages_with_ids) < original_count:
            logger.info(
                "api_defensive_deduplication_applied",
                execution_id=execution_id,
                original_count=original_count,
                deduplicated_count=len(messages_with_ids),
                removed=original_count - len(messages_with_ids),
                duplicates_by_id=duplicates_by_id,
                duplicates_by_content=duplicates_by_content
            )

        # Upsert to sessions table using SQLAlchemy
        # This matches what the streaming endpoint expects to load
        existing_session = db.query(SessionModel).filter(
            SessionModel.execution_id == execution_id
        ).first()

        if existing_session:
            # Update existing session
            existing_session.session_id = session_id
            existing_session.organization_id = organization["id"]
            existing_session.user_id = user_id
            existing_session.messages = messages_with_ids
            existing_session.metadata_ = metadata
        else:
            # Create new session
            new_session = SessionModel(
                execution_id=execution_id,
                session_id=session_id,
                organization_id=organization["id"],
                user_id=user_id,
                messages=messages_with_ids,
                metadata_=metadata,
            )
            db.add(new_session)

        db.commit()

        logger.info(
            "session_persisted_to_database",
            execution_id=execution_id,
            session_id=session_id,
            message_count=len(messages),
        )

        # Cache in Redis for hot loading on next access
        import json

        redis_client = get_redis_client()
        if redis_client:
            try:
                redis_key = f"session:{session_id}"
                cache_data = {
                    "session_id": session_id,
                    "execution_id": execution_id,
                    "messages": messages,
                    "message_count": len(messages),
                }
                await redis_client.setex(
                    redis_key,
                    3600,  # 1 hour TTL
                    json.dumps(cache_data)
                )
                logger.info(
                    "session_cached_on_write",
                    execution_id=execution_id,
                    message_count=len(messages)
                )
            except Exception as cache_error:
                logger.warning("session_cache_write_error_on_persist", error=str(cache_error))
                # Don't fail persistence if caching fails

        return {
            "success": True,
            "execution_id": execution_id,
            "session_id": session_id,
            "persisted_messages": len(messages),
        }

    except Exception as e:
        db.rollback()
        logger.error(
            "session_persistence_failed",
            error=str(e),
            execution_id=execution_id,
        )
        return {
            "success": False,
            "error": str(e),
        }


@router.post("/{execution_id}/mark-done", status_code=status.HTTP_202_ACCEPTED)
async def mark_execution_as_done(
    execution_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    """
    Mark an execution as done, signaling the workflow to complete.

    This sends a signal to the Temporal workflow to indicate the user is finished
    with the conversation. The workflow will complete gracefully after this signal.
    """
    try:
        # Get Temporal client
        temporal_client = await get_temporal_client()

        # Verify the execution belongs to this organization and get execution type
        execution = db.query(Execution).filter(
            Execution.id == uuid_module.UUID(execution_id),
            Execution.organization_id == organization["id"]
        ).first()

        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")

        # Construct workflow ID based on execution type
        execution_type = execution.execution_type or "AGENT"
        if execution_type == "TEAM":
            workflow_id = f"team-execution-{execution_id}"
        else:
            workflow_id = f"agent-execution-{execution_id}"

        workflow_handle = temporal_client.get_workflow_handle(workflow_id)

        # Send mark_as_done signal to workflow
        await workflow_handle.signal(AgentExecutionWorkflow.mark_as_done)

        logger.info(
            "execution_marked_as_done",
            execution_id=execution_id,
            org_id=organization["id"],
        )

        return {
            "success": True,
            "execution_id": execution_id,
            "message": "Execution marked as done, workflow will complete",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "mark_as_done_failed",
            error=str(e),
            execution_id=execution_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark execution as done: {str(e)}"
        )


class StreamingEventRequest(BaseModel):
    """Request to publish a streaming event to Redis for real-time UI updates"""
    event_type: str  # "status", "message", "tool_started", "tool_completed", "error"
    data: dict  # Event payload
    timestamp: str | None = None


@router.post("/{execution_id}/events", status_code=status.HTTP_202_ACCEPTED)
async def publish_execution_event(
    execution_id: str,
    event: StreamingEventRequest,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Publish a streaming event via event bus (multi-provider support).

    This endpoint is used by workers to send real-time events (tool execution, status updates, etc.)
    that are streamed to the UI via SSE without waiting for Temporal workflow completion.

    Supports multiple providers:
    - Redis: List storage + pub/sub for SSE streaming
    - HTTP: Webhook notifications
    - WebSocket: Real-time push to connected clients
    - NATS: High-performance message streaming

    Events are stored in Redis list: execution:{execution_id}:events
    TTL: 1 hour (events are temporary, final state persists in database)
    """
    try:
        # Build event payload
        event_data = {
            "event_type": event.event_type,
            "data": event.data,
            "timestamp": event.timestamp or datetime.now(timezone.utc).isoformat(),
            "execution_id": execution_id,
        }

        metadata = {
            "organization_id": organization.get("id"),
            "organization_name": organization.get("name"),
        }

        # Try to use event bus if available
        event_bus = getattr(request.app.state, 'event_bus', None)
        if event_bus:
            # Use event bus (multi-provider)
            logger.debug(
                "publishing_via_event_bus",
                execution_id=execution_id[:8],
                event_type=event.event_type,
                providers=event_bus.get_provider_names()
            )

            results = await event_bus.publish_event(
                execution_id=execution_id,
                event_type=event.event_type,
                data=event.data,
                metadata=metadata
            )

            # Log results per provider
            success_count = sum(1 for success in results.values() if success)
            logger.info(
                "execution_event_published_via_event_bus",
                execution_id=execution_id[:8],
                event_type=event.event_type,
                providers=list(results.keys()),
                success_count=success_count,
                total_providers=len(results),
                results=results
            )

            return {
                "success": success_count > 0,
                "execution_id": execution_id,
                "event_type": event.event_type,
                "providers": results
            }
        else:
            # Fallback to direct Redis (backwards compatibility)
            logger.debug(
                "event_bus_not_available_using_redis_fallback",
                execution_id=execution_id[:8],
                event_type=event.event_type
            )

            redis_client = get_redis_client()
            if not redis_client:
                # Redis not configured - skip streaming but don't fail
                logger.warning("redis_not_configured_for_streaming", execution_id=execution_id)
                return {"success": True, "message": "Redis not configured, event skipped"}

            # Push event to Redis list (most recent at head) - this must be FAST
            redis_key = f"execution:{execution_id}:events"
            await redis_client.lpush(redis_key, json.dumps(event_data))

            # Keep only last 1000 events (prevent memory issues)
            await redis_client.ltrim(redis_key, 0, 999)

            # Set TTL: 1 hour (events are temporary)
            await redis_client.expire(redis_key, 3600)

            # Also publish to pub/sub channel for real-time streaming
            # This allows connected SSE clients to receive updates instantly
            pubsub_channel = f"execution:{execution_id}:stream"
            try:
                await redis_client.publish(pubsub_channel, json.dumps(event_data))
            except Exception as pubsub_error:
                # Don't fail if pub/sub fails - the list storage is the primary mechanism
                logger.debug("pubsub_publish_failed", error=str(pubsub_error), execution_id=execution_id[:8])

            logger.info(
                "execution_event_published_via_redis_fallback",
                execution_id=execution_id[:8],
                event_type=event.event_type,
            )

            return {
                "success": True,
                "execution_id": execution_id,
                "event_type": event.event_type,
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "publish_event_failed",
            error=str(e),
            execution_id=execution_id,
            event_type=event.event_type,
        )
        # Don't fail the worker if streaming fails - it's not critical
        return {
            "success": False,
            "error": str(e),
            "message": "Event publishing failed but execution continues"
        }


@router.get("/{execution_id}/stream")
async def stream_execution(
    execution_id: str,
    request: Request,
    last_event_id: Optional[str] = None,
    organization: dict = Depends(get_current_organization),
):
    """
    Stream execution updates using Server-Sent Events (SSE).

    This endpoint combines two sources for real-time updates:
    1. Redis streaming events (from worker activities) - sub-second latency
    2. Temporal workflow queries (for state consistency) - 200ms polling

    The Redis events provide instant tool execution updates, while Temporal
    ensures we never miss state changes even if Redis is unavailable.

    Gap Recovery:
    - Supports Last-Event-ID pattern for reconnection
    - Client sends last_event_id query param or Last-Event-ID header
    - Server resumes from that point or detects gaps

    SSE format:
    - id: {execution_id}_{counter}_{timestamp_micros}
    - data: {json object with execution status, messages, tool calls}
    - event: status|message|tool_started|tool_completed|error|done
    """

    async def generate_sse():
        """Generate Server-Sent Events from Agno session and Temporal workflow state"""
        import time
        start_time = time.time()

        # Parse Last-Event-ID for gap recovery on reconnection
        # Check both query param and header (EventSource sets header automatically)
        last_known_id = last_event_id or request.headers.get("Last-Event-ID")
        last_counter = 0

        if last_known_id:
            try:
                # Parse format: {execution_id}_{counter}_{timestamp_micros}
                parts = last_known_id.split("_")
                if len(parts) >= 2 and parts[0] == execution_id:
                    last_counter = int(parts[1])
                    logger.info(
                        "reconnection_with_last_event_id",
                        execution_id=execution_id,
                        last_event_id=last_known_id,
                        last_counter=last_counter
                    )
            except (ValueError, IndexError) as e:
                logger.warning(
                    "invalid_last_event_id",
                    execution_id=execution_id,
                    last_event_id=last_known_id,
                    error=str(e)
                )
                last_counter = 0

        # Event ID counter for Last-Event-ID pattern (gap recovery)
        event_id_counter = last_counter

        def generate_event_id() -> str:
            """Generate sequential event ID for Last-Event-ID pattern"""
            nonlocal event_id_counter
            event_id_counter += 1
            # Format: {execution_id}_{counter}_{timestamp_micros}
            return f"{execution_id}_{event_id_counter}_{int(time.time() * 1000000)}"

        # Event buffer for gap recovery (sliding window)
        # Store recent events to replay on reconnection
        from collections import deque
        MAX_BUFFER_EVENTS = 100  # Max number of events to buffer
        MAX_BUFFER_SIZE = 100 * 1024  # Max 100KB of buffered data

        event_buffer = deque(maxlen=MAX_BUFFER_EVENTS)
        buffer_size = 0

        def buffer_event(event_id: str, event_type: str, data: str):
            """Add event to buffer for gap recovery"""
            nonlocal buffer_size

            event_size = len(data)
            buffer_size += event_size
            event_buffer.append((event_id, event_type, data, event_size))

            # Remove old events if buffer exceeds size limit
            while buffer_size > MAX_BUFFER_SIZE and len(event_buffer) > 1:
                _, _, _, old_size = event_buffer.popleft()
                buffer_size -= old_size

        async def replay_buffered_events():
            """Replay events from buffer starting after last_counter"""
            if not last_counter or not event_buffer:
                return

            replayed = 0
            for buf_event_id, buf_event_type, buf_data, _ in event_buffer:
                try:
                    # Parse counter from event ID: {execution_id}_{counter}_{timestamp}
                    parts = buf_event_id.split("_")
                    if len(parts) >= 2:
                        buf_counter = int(parts[1])
                        # Replay events after the last known ID
                        if buf_counter > last_counter:
                            yield f"id: {buf_event_id}\n"
                            yield f"event: {buf_event_type}\n"
                            yield f"data: {buf_data}\n\n"
                            replayed += 1
                except (ValueError, IndexError):
                    continue

            if replayed > 0:
                logger.info(
                    "replayed_buffered_events",
                    execution_id=execution_id,
                    replayed_count=replayed,
                    last_counter=last_counter
                )
            elif last_counter > 0:
                # Last event ID not in buffer - gap detected
                logger.warning(
                    "gap_detected_buffer_miss",
                    execution_id=execution_id,
                    last_counter=last_counter,
                    buffer_size=len(event_buffer)
                )
                # Notify client of gap
                event_id = generate_event_id()
                gap_data = json.dumps({
                    "last_known_id": last_known_id,
                    "reason": "Event buffer miss - events too old",
                    "buffer_oldest": event_buffer[0][0] if event_buffer else None,
                })
                yield f"id: {event_id}\n"
                yield f"event: gap_detected\n"
                yield f"data: {gap_data}\n\n"

        try:
            # Replay buffered events first if reconnecting
            if last_counter > 0:
                async for replay_chunk in replay_buffered_events():
                    yield replay_chunk
            # Check Redis cache first for execution_type (fast, sub-millisecond)
            execution_type = None
            redis_client = get_redis_client()

            if redis_client:
                try:
                    t0 = time.time()
                    # Check if we have metadata event in Redis
                    redis_key = f"execution:{execution_id}:events"
                    redis_events = await redis_client.lrange(redis_key, 0, -1)

                    # Look for metadata event with execution_type
                    if redis_events:
                        for event_json in redis_events:
                            try:
                                event_data = json.loads(event_json)
                                if event_data.get("event_type") == "metadata" and event_data.get("data", {}).get("execution_type"):
                                    execution_type = event_data["data"]["execution_type"]
                                    logger.info("timing_redis_cache_hit", duration_ms=int((time.time() - t0) * 1000), execution_id=execution_id, execution_type=execution_type)
                                    break
                            except json.JSONDecodeError:
                                continue
                except Exception as redis_error:
                    logger.warning("redis_cache_lookup_failed", error=str(redis_error), execution_id=execution_id)

            # Fall back to database if not in cache
            if not execution_type:
                t0 = time.time()
                from control_plane_api.app.database import get_session_local
                SessionLocal = get_session_local()
                db_session = SessionLocal()
                try:
                    execution_record = db_session.query(Execution).filter(
                        Execution.id == uuid_module.UUID(execution_id),
                        Execution.organization_id == organization["id"]
                    ).first()
                    logger.info("timing_db_query_fallback", duration_ms=int((time.time() - t0) * 1000), execution_id=execution_id)

                    if not execution_record:
                        raise HTTPException(status_code=404, detail="Execution not found")

                    execution_type = execution_record.execution_type or "AGENT"
                finally:
                    db_session.close()

            # Construct workflow ID based on execution type
            # Team executions use "team-execution-{id}", agent executions use "agent-execution-{id}"
            if execution_type == "TEAM":
                workflow_id = f"team-execution-{execution_id}"
            else:
                workflow_id = f"agent-execution-{execution_id}"

            # CRITICAL: Make Temporal optional - stream endpoint must work even when worker is down
            # Historical DB records and Redis streaming should work independently of Temporal
            temporal_client = None
            workflow_handle = None
            try:
                # Get Temporal client with 2-second timeout to fail fast when worker is down
                t0 = time.time()
                temporal_client = await asyncio.wait_for(
                    get_temporal_client(),
                    timeout=2.0  # Fast timeout - don't block DB history loading
                )
                logger.info("timing_temporal_client", duration_ms=int((time.time() - t0) * 1000), execution_id=execution_id)

                workflow_handle = temporal_client.get_workflow_handle(workflow_id)

                logger.info(
                    "execution_stream_connecting",
                    execution_id=execution_id,
                    execution_type=execution_type,
                    workflow_id=workflow_id,
                )
            except asyncio.TimeoutError:
                logger.warning(
                    "temporal_connection_timeout_continuing_without_workflow_queries",
                    execution_id=execution_id,
                    workflow_id=workflow_id,
                    timeout_seconds=2.0
                )
                # Continue without Temporal - DB history and Redis streaming will still work
            except Exception as temporal_error:
                logger.warning(
                    "temporal_connection_failed_continuing_without_workflow_queries",
                    execution_id=execution_id,
                    error=str(temporal_error),
                    workflow_id=workflow_id
                )
                # Continue without Temporal - DB history and Redis streaming will still work

            last_status = None
            last_message_count = 0
            last_keepalive = asyncio.get_event_loop().time()
            last_redis_event_index = -1  # Track which Redis events we've sent
            consecutive_failures = 0  # Track consecutive workflow query failures
            worker_down_mode = False  # Track if we're in worker-down fallback mode
            last_db_poll = 0  # Track last database poll time

            # CRITICAL: Track all sent message IDs to prevent duplicates across sources
            # This prevents sending the same message from both historical DB load AND Redis events
            sent_message_ids = set()  # Deduplicate across historical + Redis streaming

            # OPTIMIZATION: Cache Temporal workflow status to reduce API load
            # Only refresh status every 1 second instead of every poll (200ms)
            TEMPORAL_STATUS_CACHE_TTL = 1.0  # Cache status for 1 second
            last_temporal_status_check = 0.0
            cached_temporal_status = None
            cached_workflow_description = None

            # PERFORMANCE OPTIMIZATION: Defer Temporal workflow describe call until AFTER
            # sending historical messages. This ensures UI gets messages instantly without
            # waiting for Temporal network call (which can be slow).
            # We'll check workflow status after sending history.
            is_workflow_running = False

            # ALWAYS load historical messages from database first
            # MOVED THIS BEFORE TEMPORAL CALL FOR INSTANT MESSAGE DELIVERY
            # This ensures UI sees conversation history even when connecting mid-execution
            # In streaming mode, we'll then continue with Redis for real-time updates
            t0 = time.time()
            try:
                # Read session from Control Plane database (where worker persists)
                from control_plane_api.app.database import get_session_local
                SessionLocal = get_session_local()
                db_session = SessionLocal()
                try:
                    session_record = db_session.query(SessionModel).filter(
                        SessionModel.execution_id == execution_id,
                        SessionModel.organization_id == organization["id"]
                    ).order_by(SessionModel.updated_at.desc()).first()
                finally:
                    db_session.close()

                session_messages = []
                if session_record:
                    messages_data = session_record.messages or []

                    # OPTIMIZATION: Limit initial history load to last 200 messages
                    # This speeds up connection time for long conversations
                    # Frontend can request full history if needed via separate API
                    MAX_INITIAL_MESSAGES = 200
                    if len(messages_data) > MAX_INITIAL_MESSAGES:
                        logger.info(
                            "limiting_initial_session_history",
                            execution_id=execution_id,
                            total_messages=len(messages_data),
                            sending_count=MAX_INITIAL_MESSAGES
                        )
                        # Take the last N messages (most recent)
                        messages_data = messages_data[-MAX_INITIAL_MESSAGES:]

                    # Convert dict messages to objects with attributes
                    from dataclasses import dataclass, field
                    from typing import Optional as Opt

                    @dataclass
                    class SessionMessage:
                        role: str
                        content: Opt[str] = None  # Optional - some messages (tool/workflow) have empty content
                        timestamp: Opt[str] = None
                        message_id: Opt[str] = None
                        user_id: Opt[str] = None
                        user_name: Opt[str] = None
                        user_email: Opt[str] = None
                        user_avatar: Opt[str] = None
                        # Tool call fields
                        tool_name: Opt[str] = None
                        tool_execution_id: Opt[str] = None
                        tool_input: Opt[dict] = None
                        tool_output: Opt[Any] = None
                        tool_error: Opt[Any] = None
                        tool_status: Opt[str] = None
                        # Streaming state
                        is_streaming: Opt[bool] = None
                        # Metadata (team members, etc.)
                        metadata: Opt[dict] = None
                        # Workflow fields
                        workflow_name: Opt[str] = None
                        workflow_status: Opt[str] = None
                        workflow_steps: Opt[list] = None
                        workflow_runner: Opt[str] = None
                        workflow_type: Opt[str] = None
                        workflow_duration: Opt[float] = None
                        workflow_error: Opt[str] = None

                    session_messages = [SessionMessage(**{k: v for k, v in msg.items() if k in SessionMessage.__annotations__}) for msg in messages_data]

                    # CRITICAL: Sort messages by timestamp to ensure chronological order
                    # Messages must be in exact order for proper conversation flow
                    # Parse timestamps as datetime for accurate sorting (handles different formats)
                    def parse_timestamp(ts):
                        if not ts:
                            return datetime.min
                        try:
                            # Handle both formats: with and without timezone
                            return datetime.fromisoformat(ts.replace('Z', '+00:00'))
                        except:
                            return datetime.min
                    # DEBUG: Log timestamps BEFORE sorting
                    logger.info(
                        "messages_before_sort",
                        execution_id=execution_id,
                        sample_messages=[
                            {
                                "role": m.role,
                                "timestamp": m.timestamp,
                                "parsed": parse_timestamp(m.timestamp).isoformat() if m.timestamp else "NONE"
                            }
                            for m in session_messages[:5]  # First 5 messages
                        ]
                    )

                    session_messages.sort(key=lambda m: parse_timestamp(m.timestamp))

                    # DEBUG: Log timestamps AFTER sorting
                    logger.info(
                        "sorted_session_messages_by_timestamp",
                        execution_id=execution_id,
                        message_count=len(session_messages),
                        first_timestamp=session_messages[0].timestamp if session_messages else None,
                        last_timestamp=session_messages[-1].timestamp if session_messages else None,
                        first_messages=[
                            {"role": m.role, "timestamp": m.timestamp, "content": (m.content or "")[:50]}
                            for m in session_messages[:5]  # First 5 after sort
                        ]
                    )

                    # BACKWARD COMPATIBILITY: Normalize old message ID formats
                    # New format: {execution_id}_{role}_{turn_number} (deterministic, turn-based)
                    # Old formats: {execution_id}_{role}_{idx} or {execution_id}_{timestamp_micros}
                    # We use content hash for old messages to ensure stable IDs across reloads
                    import hashlib
                    normalized_count = 0
                    for msg in session_messages:
                        if not msg.message_id:
                            continue

                        parts = msg.message_id.split("_")
                        # Check if already in new turn-based format: {exec_id}_{role}_{small_number}
                        # Turn numbers are typically small (1-100), while timestamps are huge (1e15)
                        if len(parts) >= 3 and parts[-2] in ["user", "assistant"]:
                            try:
                                last_part = int(parts[-1])
                                # If last part is small, likely a turn number (new format)
                                # If last part is huge, likely a timestamp (old format)
                                if last_part < 10000:
                                    # Already in new format, keep as-is
                                    continue
                            except (ValueError, IndexError):
                                # Can't parse last part as number, might be hash or other format
                                pass

                        # Old format detected - use content hash for stable ID
                        # This prevents duplicates when old sessions are reloaded
                        content_hash = hashlib.md5((msg.content or "").encode()).hexdigest()[:8]
                        old_id = msg.message_id
                        msg.message_id = f"{execution_id}_{msg.role}_{content_hash}"
                        normalized_count += 1
                        logger.debug(
                            "normalized_old_message_id_format",
                            execution_id=execution_id,
                            old_id=old_id,
                            new_id=msg.message_id,
                            role=msg.role
                        )

                    if normalized_count > 0:
                        logger.info(
                            "normalized_message_ids_for_backward_compatibility",
                            execution_id=execution_id,
                            normalized_count=normalized_count,
                            total_messages=len(session_messages)
                        )

                if session_messages:
                    logger.info(
                        "sending_session_history_on_connect",
                        execution_id=execution_id,
                        message_count=len(session_messages)
                    )

                    # Send all existing messages immediately with ALL fields preserved
                    for msg in session_messages:
                        # CRITICAL: Skip messages with empty content UNLESS they have tool/workflow data
                        # Tool messages have empty content but contain tool_name, tool_input, tool_output, etc.
                        # Workflow messages have empty content but contain workflow_name, workflow_steps, etc.
                        has_content = msg.content and msg.content.strip()
                        has_tool_data = (
                            getattr(msg, 'tool_name', None) or
                            getattr(msg, 'tool_input', None) or
                            getattr(msg, 'tool_output', None) or
                            getattr(msg, 'tool_error', None)
                        )
                        has_workflow_data = (
                            getattr(msg, 'workflow_name', None) or
                            getattr(msg, 'workflow_steps', None)
                        )

                        if not has_content and not has_tool_data and not has_workflow_data:
                            logger.debug(
                                "skipping_empty_historical_message",
                                execution_id=execution_id,
                                role=msg.role,
                                timestamp=msg.timestamp,
                                message_id=getattr(msg, 'message_id', None)
                            )
                            continue

                        # CRITICAL: Ensure every message has a message_id
                        # Generate one if missing to enable proper deduplication on frontend
                        message_id = msg.message_id
                        if not message_id:
                            # Generate stable message_id from timestamp and role
                            # This ensures same message gets same ID on reconnect
                            try:
                                if msg.timestamp:
                                    timestamp_micros = int(datetime.fromisoformat(msg.timestamp.replace('Z', '+00:00')).timestamp() * 1000000)
                                else:
                                    timestamp_micros = int(time.time() * 1000000)
                            except Exception as ts_error:
                                logger.warning(
                                    "failed_to_parse_timestamp_for_message_id",
                                    execution_id=execution_id,
                                    timestamp=msg.timestamp,
                                    error=str(ts_error)
                                )
                                timestamp_micros = int(time.time() * 1000000)

                            message_id = f"{execution_id}_{msg.role}_{timestamp_micros}"
                            logger.info(
                                "generated_message_id_for_historical_message",
                                execution_id=execution_id,
                                role=msg.role,
                                timestamp=msg.timestamp,
                                generated_id=message_id,
                                has_content=bool(msg.content and msg.content.strip())
                            )
                        else:
                            logger.debug(
                                "using_existing_message_id",
                                execution_id=execution_id,
                                role=msg.role,
                                message_id=message_id
                            )

                        # CRITICAL: Check if this message was already sent (deduplication)
                        # This prevents duplicates when messages appear in both DB history and Redis events
                        if message_id in sent_message_ids:
                            logger.debug(
                                "skipping_duplicate_historical_message",
                                execution_id=execution_id,
                                message_id=message_id,
                                role=msg.role
                            )
                            continue

                        # Track that we've sent this message
                        sent_message_ids.add(message_id)

                        msg_data = {
                            "role": msg.role,
                            "content": msg.content or "",  # Ensure content is never None
                            "timestamp": msg.timestamp,  # Already in ISO format from database
                            "message_id": message_id,  # Always include message_id (generated or from msg)
                        }

                        # Include all optional fields if available
                        optional_fields = [
                            "user_id", "user_name", "user_email", "user_avatar",
                            "tool_name", "tool_execution_id", "tool_input", "tool_output",
                            "tool_error", "tool_status", "is_streaming", "metadata",
                            "workflow_name", "workflow_status", "workflow_steps",
                            "workflow_runner", "workflow_type", "workflow_duration", "workflow_error"
                        ]

                        for field in optional_fields:
                            value = getattr(msg, field, None)
                            if value is not None:
                                msg_data[field] = value

                        event_id = generate_event_id()
                        yield f"id: {event_id}\n"
                        yield f"event: message\n"
                        yield f"data: {json.dumps(msg_data)}\n\n"

                    last_message_count = len(session_messages)

                logger.info("timing_session_history_load", duration_ms=int((time.time() - t0) * 1000), execution_id=execution_id, message_count=last_message_count)

            except Exception as session_error:
                    logger.warning(
                        "failed_to_load_session_history",
                        execution_id=execution_id,
                        error=str(session_error),
                        duration_ms=int((time.time() - t0) * 1000)
                    )
                    # Continue even if session loading fails - workflow state will still work

            # FALLBACK: If no session history was loaded (empty, missing, or failed),
            # try to get conversation history from Temporal workflow state
            # This ensures clients ALWAYS receive conversation history even if:
            # - Session hasn't been persisted to database yet
            # - Session data was lost/cleared
            # - Database query failed
            if last_message_count == 0 and workflow_handle is not None:
                try:
                    logger.info(
                        "no_session_history_attempting_workflow_fallback",
                        execution_id=execution_id
                    )
                    t0 = time.time()

                    # Query workflow state to get messages with 3-second timeout
                    # Prevents 29-second hang when worker is down
                    try:
                        state = await asyncio.wait_for(
                            workflow_handle.query(AgentExecutionWorkflow.get_state),
                            timeout=3.0
                        )
                    except asyncio.TimeoutError:
                        logger.warning(
                            "workflow_fallback_timeout",
                            execution_id=execution_id,
                            timeout_seconds=3.0,
                            duration_ms=int((time.time() - t0) * 1000)
                        )
                        state = None

                    if state and state.messages and len(state.messages) > 0:
                        logger.info(
                            "workflow_fallback_found_messages",
                            execution_id=execution_id,
                            message_count=len(state.messages)
                        )

                        # Send all messages from workflow state
                        for msg in state.messages:
                            # Skip empty messages without tool/workflow data
                            has_content = msg.content and msg.content.strip()
                            has_tool_data = bool(msg.tool_name or getattr(msg, 'tool_input', None) or getattr(msg, 'tool_output', None))

                            if not has_content and not has_tool_data:
                                continue

                            # Generate message_id if missing
                            message_id = getattr(msg, 'message_id', None)
                            if not message_id:
                                try:
                                    if msg.timestamp:
                                        timestamp_micros = int(datetime.fromisoformat(msg.timestamp.replace('Z', '+00:00')).timestamp() * 1000000)
                                    else:
                                        timestamp_micros = int(time.time() * 1000000)
                                except:
                                    timestamp_micros = int(time.time() * 1000000)

                                message_id = f"{execution_id}_{msg.role}_{timestamp_micros}"

                            # CRITICAL: Deduplicate workflow fallback messages too
                            if message_id in sent_message_ids:
                                logger.debug(
                                    "skipping_duplicate_workflow_fallback_message",
                                    execution_id=execution_id,
                                    message_id=message_id
                                )
                                continue

                            sent_message_ids.add(message_id)

                            msg_data = {
                                "role": msg.role,
                                "content": msg.content or "",
                                "timestamp": msg.timestamp,
                                "message_id": message_id,
                            }

                            # Include optional fields
                            if msg.tool_name:
                                msg_data["tool_name"] = msg.tool_name
                                msg_data["tool_input"] = getattr(msg, 'tool_input', None)
                                msg_data["tool_output"] = getattr(msg, 'tool_output', None)
                                msg_data["tool_error"] = getattr(msg, 'tool_error', None)
                                msg_data["tool_status"] = getattr(msg, 'tool_status', None)

                            # Include user attribution
                            if hasattr(msg, 'user_id') and msg.user_id:
                                msg_data["user_id"] = msg.user_id
                                msg_data["user_name"] = getattr(msg, 'user_name', None)
                                msg_data["user_email"] = getattr(msg, 'user_email', None)
                                msg_data["user_avatar"] = getattr(msg, 'user_avatar', None)

                            event_id = generate_event_id()
                            yield f"id: {event_id}\n"
                            yield f"event: message\n"
                            yield f"data: {json.dumps(msg_data)}\n\n"

                        last_message_count = len(state.messages)
                        logger.info(
                            "workflow_fallback_history_sent",
                            execution_id=execution_id,
                            message_count=last_message_count,
                            duration_ms=int((time.time() - t0) * 1000)
                        )
                    else:
                        logger.info(
                            "workflow_fallback_no_messages",
                            execution_id=execution_id
                        )

                except Exception as workflow_fallback_error:
                    logger.warning(
                        "workflow_fallback_failed",
                        execution_id=execution_id,
                        error=str(workflow_fallback_error),
                        duration_ms=int((time.time() - t0) * 1000)
                    )
                    # Continue even if workflow fallback fails

            # Send history_complete event to signal that all historical messages have been loaded
            # This allows the frontend to stop showing loading state and start processing real-time updates
            # Wrapped in try/except to guarantee event is sent even if there's an error
            try:
                logger.info(
                    "about_to_send_history_complete",
                    execution_id=execution_id,
                    message_count=last_message_count
                )

                event_id = generate_event_id()
                history_complete_data = {
                    "execution_id": execution_id,
                    "message_count": last_message_count,
                    "is_truncated": False,
                    "has_more": False
                }
                yield f"id: {event_id}\n"
                yield f"event: history_complete\n"
                yield f"data: {json.dumps(history_complete_data)}\n\n"

                logger.info(
                    "history_complete_sent",
                    execution_id=execution_id,
                    message_count=last_message_count,
                    event_data=history_complete_data
                )
            except Exception as history_complete_error:
                # Log error but don't fail the stream - try to send basic event
                logger.error(
                    "history_complete_send_failed",
                    execution_id=execution_id,
                    error=str(history_complete_error)
                )
                # Still try to send a minimal history_complete event
                try:
                    yield f"event: history_complete\n"
                    yield f"data: {json.dumps({'execution_id': execution_id, 'message_count': 0})}\n\n"
                except:
                    # If even this fails, continue without it
                    pass

            # NOW check workflow status via Temporal (after messages sent for instant UX)
            # Check if worker is ACTIVELY processing by checking Temporal workflow execution status
            # This is much more performant than querying workflow state - it's just a metadata lookup
            # We only stream from Redis if workflow is RUNNING at Temporal level (worker is active)
            # Otherwise, we load from database (workflow completed/failed/no active worker)
            if workflow_handle is not None:
                try:
                    t0 = time.time()
                    description = await workflow_handle.describe()
                    # Temporal execution status: RUNNING, COMPLETED, FAILED, CANCELLED, TERMINATED, TIMED_OUT, CONTINUED_AS_NEW
                    # Use .name to get just the enum name (e.g., "RUNNING") without the class prefix
                    temporal_status_name = description.status.name
                    is_workflow_running = temporal_status_name == "RUNNING"

                    # Initialize cache with initial status
                    cached_temporal_status = temporal_status_name
                    cached_workflow_description = description
                    last_temporal_status_check = t0

                    logger.info(
                        "initial_workflow_status",
                        execution_id=execution_id,
                        temporal_status=temporal_status_name,
                        temporal_status_full=str(description.status),
                        is_running=is_workflow_running,
                        duration_ms=int((time.time() - t0) * 1000)
                    )
                except Exception as describe_error:
                    # If we can't describe workflow, assume it's not running
                    logger.warning("initial_workflow_describe_failed", execution_id=execution_id, error=str(describe_error))
                    is_workflow_running = False
            else:
                # No workflow handle available - worker is down
                logger.info("no_workflow_handle_worker_down", execution_id=execution_id)
                is_workflow_running = False

            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    logger.info("execution_stream_disconnected", execution_id=execution_id)
                    break

                # CRITICAL: Graceful shutdown before Vercel 300s timeout
                # Calculate remaining time (270s = 4.5min with 30s buffer)
                MAX_STREAM_DURATION = 270  # 30-second safety buffer before Vercel timeout
                elapsed = time.time() - start_time
                remaining = MAX_STREAM_DURATION - elapsed

                if remaining <= 0:
                    logger.info(
                        "approaching_timeout_graceful_shutdown",
                        execution_id=execution_id,
                        elapsed=elapsed
                    )
                    # Tell client to reconnect gracefully (won't count as failed attempt)
                    event_id = generate_event_id()
                    yield f"id: {event_id}\n"
                    yield f"event: reconnect\n"
                    yield f"data: {json.dumps({'reason': 'timeout', 'duration': elapsed})}\n\n"
                    break

                # Countdown warnings in last 30 seconds
                if remaining <= 30 and remaining % 10 < 0.2:
                    event_id = generate_event_id()
                    yield f"id: {event_id}\n"
                    yield f"event: timeout_warning\n"
                    yield f"data: {json.dumps({'remaining_seconds': int(remaining)})}\n\n"

                # Send keepalive comment every 15 seconds to prevent timeout
                current_time = asyncio.get_event_loop().time()
                if current_time - last_keepalive > 15:
                    yield ": keepalive\n\n"
                    last_keepalive = current_time

                # FIRST: Check Redis for NEW real-time streaming events (sub-second latency)
                # ONLY if workflow is actively running (worker is connected and processing)
                # We track which events we've sent to avoid re-sending
                if is_workflow_running and redis_client:
                    try:
                        redis_key = f"execution:{execution_id}:events"
                        # Get the total count of events in Redis
                        total_events = await redis_client.llen(redis_key)

                        if total_events and total_events > (last_redis_event_index + 1):
                            # There are new events we haven't sent yet
                            logger.debug(
                                "redis_new_events_found",
                                execution_id=execution_id,
                                total=total_events,
                                last_index=last_redis_event_index
                            )

                            # Get all events (they're in reverse chronological order from LPUSH)
                            all_redis_events = await redis_client.lrange(redis_key, 0, -1)

                            if all_redis_events:
                                # Reverse to get chronological order (oldest first)
                                chronological_events = list(reversed(all_redis_events))

                                # Send only NEW events we haven't sent yet
                                for i in range(last_redis_event_index + 1, len(chronological_events)):
                                    event_json = chronological_events[i]

                                    try:
                                        event_data = json.loads(event_json)
                                        event_type = event_data.get("event_type", "message")

                                        # Build payload matching frontend schema expectations
                                        # Two different structures based on event type:
                                        # 1. "message" events: flat structure with role, content, etc. (MessageEventSchema)
                                        # 2. Other events: nested {data: {...}, timestamp: "..."} (MessageChunkEventSchema, etc.)
                                        if "data" in event_data and isinstance(event_data["data"], dict):
                                            if event_type == "message" and "role" in event_data["data"]:
                                                # Message events expect flat structure: {role, content, timestamp, ...}
                                                payload = event_data["data"]
                                            else:
                                                # Chunk events and others expect nested: {data: {...}, timestamp: "..."}
                                                # This applies to: message_chunk, member_message_chunk, tool_started, etc.
                                                payload = {
                                                    "data": event_data["data"],
                                                    "timestamp": event_data.get("timestamp")
                                                }
                                        else:
                                            # Fallback for legacy format or malformed events
                                            payload = event_data

                                        # CRITICAL: Ensure every MESSAGE event has a message_id
                                        # Generate one if missing (same as historical messages)
                                        if event_type == "message" and isinstance(payload, dict) and "role" in payload:
                                            if not payload.get("message_id"):
                                                # Generate stable message_id from timestamp and role
                                                timestamp = payload.get("timestamp") or event_data.get("timestamp")
                                                role = payload.get("role", "unknown")

                                                if timestamp:
                                                    try:
                                                        timestamp_micros = int(datetime.fromisoformat(timestamp.replace('Z', '+00:00')).timestamp() * 1000000)
                                                    except:
                                                        timestamp_micros = int(time.time() * 1000000)
                                                else:
                                                    timestamp_micros = int(time.time() * 1000000)

                                                generated_id = f"{execution_id}_{role}_{timestamp_micros}"
                                                payload["message_id"] = generated_id

                                                logger.debug(
                                                    "generated_message_id_for_redis_event",
                                                    execution_id=execution_id,
                                                    role=role,
                                                    timestamp=timestamp,
                                                    generated_id=generated_id
                                                )

                                        # CRITICAL: Deduplicate Redis events (especially "message" type)
                                        # Skip if we already sent this message from historical DB load
                                        redis_message_id = payload.get("message_id") if isinstance(payload, dict) else None
                                        if redis_message_id and redis_message_id in sent_message_ids:
                                            logger.debug(
                                                "skipping_duplicate_redis_event",
                                                execution_id=execution_id,
                                                event_type=event_type,
                                                message_id=redis_message_id
                                            )
                                            # Still update index to mark as processed
                                            last_redis_event_index = i
                                            continue

                                        # Track sent message IDs
                                        if redis_message_id:
                                            sent_message_ids.add(redis_message_id)

                                        # Stream the event to UI with event ID for gap recovery
                                        event_id = generate_event_id()
                                        yield f"id: {event_id}\n"
                                        yield f"event: {event_type}\n"
                                        yield f"data: {json.dumps(payload)}\n\n"

                                        last_redis_event_index = i

                                        logger.debug(
                                            "redis_event_streamed",
                                            execution_id=execution_id,
                                            event_type=event_type,
                                            index=i
                                        )

                                    except json.JSONDecodeError as e:
                                        logger.warning("invalid_redis_event_json", event=event_json[:100], error=str(e))
                                        continue
                                    except Exception as e:
                                        logger.error("redis_event_processing_error", event=event_json[:100], error=str(e))
                                        continue

                    except Exception as redis_error:
                        logger.error("redis_event_read_failed", error=str(redis_error), execution_id=execution_id)
                        # Notify client of degraded state (Redis unavailable, falling back to Temporal polling)
                        event_id = generate_event_id()
                        degraded_data = json.dumps({
                            "reason": "redis_unavailable",
                            "fallback": "temporal_polling",
                            "message": "Real-time events unavailable, using workflow polling (slower updates)"
                        })
                        yield f"id: {event_id}\n"
                        yield f"event: degraded\n"
                        yield f"data: {degraded_data}\n\n"
                        # Continue with Temporal polling even if Redis fails

                # SECOND: Check Temporal workflow execution status (lightweight metadata lookup)
                # Skip if workflow_handle is None (worker down)
                if workflow_handle is not None:
                    try:
                        # OPTIMIZATION: Use cached status if within TTL (1 second) to reduce Temporal API load
                        current_time = time.time()
                        if cached_temporal_status and (current_time - last_temporal_status_check) < TEMPORAL_STATUS_CACHE_TTL:
                            # Use cached status
                            temporal_status = cached_temporal_status
                            description = cached_workflow_description
                            describe_duration = 0  # Cached, no API call
                        else:
                            # Cache expired or not set, fetch fresh status
                            t0 = time.time()
                            description = await workflow_handle.describe()
                            temporal_status = description.status.name  # Get enum name (e.g., "RUNNING")
                            describe_duration = int((time.time() - t0) * 1000)

                            # Update cache
                            cached_temporal_status = temporal_status
                            cached_workflow_description = description
                            last_temporal_status_check = t0

                            # Log slow describe calls (>100ms)
                            if describe_duration > 100:
                                logger.warning("slow_temporal_describe", duration_ms=describe_duration, execution_id=execution_id)

                        # Update is_workflow_running based on Temporal execution status
                        # Only stream from Redis when workflow is actively being processed by a worker
                        previous_running_state = is_workflow_running
                        is_workflow_running = temporal_status == "RUNNING"

                        # Log when streaming mode changes
                        if previous_running_state != is_workflow_running:
                            logger.info(
                                "streaming_mode_changed",
                                execution_id=execution_id,
                                temporal_status=temporal_status,
                                is_workflow_running=is_workflow_running,
                                mode="redis_streaming" if is_workflow_running else "database_only"
                            )

                        # If workflow finished, send appropriate event and exit
                        if temporal_status in ["COMPLETED", "FAILED", "TERMINATED", "CANCELLED"]:
                            # Query workflow state one final time to get the complete results
                            try:
                                state = await workflow_handle.query(AgentExecutionWorkflow.get_state)

                                if temporal_status in ["COMPLETED", "TERMINATED"]:
                                    done_data = {
                                        "execution_id": execution_id,
                                        "status": "completed",
                                        "response": state.current_response,
                                        "usage": state.usage,
                                        "metadata": state.metadata,
                                    }
                                    event_id = generate_event_id()
                                    yield f"id: {event_id}\n"
                                    yield f"event: done\n"
                                    yield f"data: {json.dumps(done_data)}\n\n"
                                else:  # FAILED or CANCELLED
                                    error_data = {
                                        "error": state.error_message or f"Workflow {temporal_status.lower()}",
                                        "execution_id": execution_id,
                                        "status": "failed",
                                    }
                                    if state.metadata.get("error_type"):
                                        error_data["error_type"] = state.metadata["error_type"]
                                    event_id = generate_event_id()
                                    yield f"id: {event_id}\n"
                                    yield f"event: error\n"
                                    yield f"data: {json.dumps(error_data)}\n\n"
                            except Exception as final_query_error:
                                # If we can't query for final state, fall back to database
                                logger.warning("final_state_query_failed", execution_id=execution_id, error=str(final_query_error))

                                # Try to get final status from database
                                try:
                                    from control_plane_api.app.database import get_session_local
                                    SessionLocal = get_session_local()
                                    db_session = SessionLocal()
                                    try:
                                        exec_record = db_session.query(Execution).filter(
                                            Execution.id == uuid_module.UUID(execution_id)
                                        ).first()
                                    finally:
                                        db_session.close()

                                    if exec_record:
                                        if temporal_status in ["COMPLETED", "TERMINATED"]:
                                            done_data = {
                                                "execution_id": execution_id,
                                                "status": exec_record.status or "completed",
                                                "response": exec_record.response,
                                                "usage": exec_record.usage or {},
                                                "metadata": exec_record.execution_metadata or {},
                                            }
                                            event_id = generate_event_id()
                                            yield f"id: {event_id}\n"
                                            yield f"event: done\n"
                                            yield f"data: {json.dumps(done_data)}\n\n"
                                        else:
                                            error_data = {
                                                "error": exec_record.error_message or f"Workflow {temporal_status.lower()}",
                                                "execution_id": execution_id,
                                                "status": exec_record.status or "failed",
                                            }
                                            event_id = generate_event_id()
                                            yield f"id: {event_id}\n"
                                            yield f"event: error\n"
                                            yield f"data: {json.dumps(error_data)}\n\n"
                                    else:
                                        event_id = generate_event_id()
                                        yield f"id: {event_id}\n"
                                        yield f"event: done\n"
                                        yield f"data: {json.dumps({'execution_id': execution_id, 'workflow_status': temporal_status})}\n\n"
                                except Exception as db_error:
                                    logger.error("database_fallback_failed", execution_id=execution_id, error=str(db_error))
                                    event_id = generate_event_id()
                                    yield f"id: {event_id}\n"
                                    yield f"event: done\n"
                                    yield f"data: {json.dumps({'execution_id': execution_id, 'workflow_status': temporal_status})}\n\n"
                            break

                        # THIRD: Query workflow state for application-level details (messages, usage, etc.)
                        # Only do this if workflow is still running to get incremental updates
                        try:
                            state = await workflow_handle.query(AgentExecutionWorkflow.get_state)

                            # Reset failure counter on successful query
                            if consecutive_failures > 0:
                                    logger.info(
                                    "workflow_query_recovered",
                                    execution_id=execution_id,
                                    failures=consecutive_failures
                                )
                            consecutive_failures = 0
                            worker_down_mode = False
    
                            # Send status update if changed
                            if state.status != last_status:
                                event_id = generate_event_id()
                                yield f"id: {event_id}\n"
                                yield f"event: status\n"
                                yield f"data: {json.dumps({'status': state.status, 'execution_id': execution_id})}\n\n"
                                last_status = state.status
    
                                logger.info(
                                    "execution_status_update",
                                    execution_id=execution_id,
                                    status=state.status
                                )
    
                            # Send new messages incrementally
                            # Skip assistant messages - they're already streamed via message_chunk events
                            if len(state.messages) > last_message_count:
                                new_messages = state.messages[last_message_count:]
                                for msg in new_messages:
                                    # Skip assistant messages to prevent duplicates with chunk streaming
                                    if msg.role == "assistant":
                                        continue
    
                                    msg_data = {
                                        "role": msg.role,
                                        "content": msg.content,
                                        "timestamp": msg.timestamp,
                                    }
                                    if msg.tool_name:
                                        msg_data["tool_name"] = msg.tool_name
                                        msg_data["tool_input"] = msg.tool_input
                                        msg_data["tool_output"] = msg.tool_output
                                    # Include user attribution for messages
                                    if hasattr(msg, 'user_id') and msg.user_id:
                                        msg_data["user_id"] = msg.user_id
                                        msg_data["user_name"] = msg.user_name
                                        msg_data["user_email"] = msg.user_email
                                        msg_data["user_avatar"] = msg.user_avatar
    
                                    event_id = generate_event_id()
                                    yield f"id: {event_id}\n"
                                    yield f"event: message\n"
                                    yield f"data: {json.dumps(msg_data)}\n\n"
    
                                last_message_count = len(state.messages)
    
                        except Exception as query_error:
                            # Workflow query failed - track failures and switch to database fallback
                            consecutive_failures += 1
                            error_msg = str(query_error)
    
                            # Detect worker down condition
                            is_worker_down = "no poller seen" in error_msg or "workflow not found" in error_msg
    
                            # Switch to database fallback after 2 consecutive failures (faster detection)
                            if consecutive_failures >= 2 and not worker_down_mode:
                                worker_down_mode = True
                                logger.warning(
                                    "worker_down_detected_switching_to_database_mode",
                                    execution_id=execution_id,
                                    failures=consecutive_failures,
                                    error=error_msg
                                )
                                # Notify client of degraded state (worker down, falling back to database)
                                event_id = generate_event_id()
                                degraded_data = json.dumps({
                                    "reason": "worker_unavailable",
                                    "fallback": "database_polling",
                                    "message": "Worker unavailable, using database polling (slower updates)"
                                })
                                yield f"id: {event_id}\n"
                                yield f"event: degraded\n"
                                yield f"data: {degraded_data}\n\n"
    
                            # In worker down mode, poll database for updates
                            if worker_down_mode:
                                current_time = time.time()
                                # Poll database every 2 seconds when worker is down
                                if current_time - last_db_poll >= 2.0:
                                    try:
                                        # Check execution status from database
                                        from control_plane_api.app.database import get_session_local
                                        SessionLocal = get_session_local()
                                        db_session = SessionLocal()
                                        try:
                                            exec_record = db_session.query(Execution).filter(
                                                Execution.id == uuid_module.UUID(execution_id)
                                            ).first()
                                        finally:
                                            db_session.close()

                                        if exec_record:
                                            db_status = exec_record.status

                                            # Send status update if changed
                                            if db_status and db_status != last_status:
                                                event_id = generate_event_id()
                                                yield f"id: {event_id}\n"
                                                yield f"event: status\n"
                                                yield f"data: {json.dumps({'status': db_status, 'execution_id': execution_id, 'source': 'database'})}\n\n"
                                                last_status = db_status

                                                logger.info(
                                                    "database_status_update",
                                                    execution_id=execution_id,
                                                    status=db_status
                                                )

                                            # Check if execution finished
                                            if db_status in ["completed", "failed", "cancelled"]:
                                                if db_status == "completed":
                                                    done_data = {
                                                        "execution_id": execution_id,
                                                        "status": db_status,
                                                        "response": exec_record.response,
                                                    }
                                                    event_id = generate_event_id()
                                                    yield f"id: {event_id}\n"
                                                    yield f"event: done\n"
                                                    yield f"data: {json.dumps(done_data)}\n\n"
                                                else:
                                                    error_data = {
                                                        "error": exec_record.error_message or f"Execution {db_status}",
                                                        "execution_id": execution_id,
                                                        "status": db_status,
                                                    }
                                                    event_id = generate_event_id()
                                                    yield f"id: {event_id}\n"
                                                    yield f"event: error\n"
                                                    yield f"data: {json.dumps(error_data)}\n\n"
                                                break

                                        # Check for new session messages
                                        db_session2 = SessionLocal()
                                        try:
                                            session_record = db_session2.query(SessionModel).filter(
                                                SessionModel.execution_id == execution_id,
                                                SessionModel.organization_id == organization["id"]
                                            ).first()
                                        finally:
                                            db_session2.close()

                                        if session_record:
                                            db_messages = session_record.messages or []
                                            if len(db_messages) > last_message_count:
                                                new_messages = db_messages[last_message_count:]
                                                for msg_dict in new_messages:
                                                    event_id = generate_event_id()
                                                    yield f"id: {event_id}\n"
                                                    yield f"event: message\n"
                                                    yield f"data: {json.dumps(msg_dict)}\n\n"
                                                last_message_count = len(db_messages)

                                                logger.info(
                                                    "database_messages_update",
                                                    execution_id=execution_id,
                                                    new_messages=len(new_messages)
                                                )

                                        last_db_poll = current_time

                                    except Exception as db_poll_error:
                                        logger.error(
                                            "database_poll_failed",
                                            execution_id=execution_id,
                                            error=str(db_poll_error)
                                        )
                            else:
                                # Still trying to connect to worker - log but don't switch modes yet
                                logger.debug(
                                    "workflow_query_failed",
                                    execution_id=execution_id,
                                    failures=consecutive_failures,
                                    error=error_msg
                                )
    
                        # Poll every 200ms for real-time updates when worker is up
                        # Poll every 500ms when in worker down mode (database polling)
                        await asyncio.sleep(0.5 if worker_down_mode else 0.2)

                    except Exception as error:
                        # Critical error (e.g., workflow describe failed)
                        logger.error(
                            "critical_streaming_error",
                            execution_id=execution_id,
                            error=str(error)
                        )
                        # Back off and retry
                        await asyncio.sleep(1.0)
            else:
                # workflow_handle is None - worker down, just poll database periodically
                await asyncio.sleep(2.0)

        except Exception as e:
            logger.error("execution_stream_error", error=str(e), execution_id=execution_id)
            event_id = generate_event_id()
            yield f"id: {event_id}\n"
            yield f"event: error\n"
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate_sse(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@router.post("/{execution_id}/job/{job_id}/status")
async def update_job_execution_status_v2(
    execution_id: str,
    job_id: str,
    request_data: UpdateJobExecutionStatusRequest,
    request: Request,
    organization: dict = Depends(get_current_organization),
    db: Session = Depends(get_db),
):
    """
    Update job_executions record with execution results.

    This endpoint is used by workers to update job execution status via HTTP
    instead of directly accessing the database.
    """
    try:
        from datetime import timezone

        now = datetime.now(timezone.utc).isoformat()

        logger.info(
            "updating_job_execution_status",
            job_id=job_id,
            execution_id=execution_id,
            status=request_data.status,
        )

        # Update job_executions record
        job_execution = db.query(JobExecution).filter(
            JobExecution.job_id == job_id,
            JobExecution.execution_id == uuid_module.UUID(execution_id)
        ).first()

        if job_execution:
            job_execution.execution_status = request_data.status
            job_execution.execution_duration_ms = request_data.duration_ms
            db.commit()

        # Update job success/failure counts
        if request_data.status == "completed":
            # Increment successful_executions - SECURITY: Add org_id filter
            try:
                job = db.query(Job).filter(
                    Job.id == job_id,
                    Job.organization_id == organization["id"]
                ).first()
                if job:
                    job.successful_executions = (job.successful_executions or 0) + 1
                    db.commit()
            except Exception as e:
                db.rollback()
                logger.warning("failed_to_increment_success_count", job_id=job_id, error=str(e))

        elif request_data.status == "failed":
            # Increment failed_executions - SECURITY: Add org_id filter
            try:
                job = db.query(Job).filter(
                    Job.id == job_id,
                    Job.organization_id == organization["id"]
                ).first()
                if job:
                    job.failed_executions = (job.failed_executions or 0) + 1
                    db.commit()
            except Exception as e:
                db.rollback()
                logger.warning("failed_to_increment_failure_count", job_id=job_id, error=str(e))

        logger.info(
            "updated_job_execution_status",
            job_id=job_id,
            execution_id=execution_id,
            status=request_data.status,
        )

        # Publish event to Redis for real-time UI updates
        try:
            redis_client = get_redis_client()
            if redis_client:
                event_type = "done" if request_data.status == "completed" else "error"
                event_data = {
                    "event_type": event_type,
                    "data": {
                        "job_id": job_id,
                        "execution_id": execution_id,
                        "status": request_data.status,
                        "duration_ms": request_data.duration_ms,
                        "error_message": request_data.error_message,
                        "message": f"Job execution {request_data.status}",
                    },
                    "timestamp": now,
                    "execution_id": execution_id,
                }

                # Push to Redis list
                redis_key = f"execution:{execution_id}:events"
                await redis_client.lpush(redis_key, json.dumps(event_data))
                await redis_client.ltrim(redis_key, 0, 999)
                await redis_client.expire(redis_key, 3600)

                # Publish to pub/sub for real-time streaming
                pubsub_channel = f"execution:{execution_id}:stream"
                await redis_client.publish(pubsub_channel, json.dumps(event_data))

                logger.info(
                    "job_status_event_published",
                    execution_id=execution_id[:8],
                    job_id=job_id[:8],
                    event_type=event_type,
                )
        except Exception as event_error:
            # Don't fail the request if event publishing fails
            logger.warning(
                "failed_to_publish_job_status_event",
                job_id=job_id,
                execution_id=execution_id,
                error=str(event_error),
            )

        return {
            "job_id": job_id,
            "execution_id": execution_id,
            "status": "updated",
        }

    except Exception as e:
        db.rollback()
        logger.error(
            "failed_to_update_job_execution_status",
            job_id=job_id,
            execution_id=execution_id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update job execution status: {str(e)}"
        )


# ============================================================================
# State Transition Endpoints
# ============================================================================


class StateOverrideRequest(BaseModel):
    """Request to manually override execution state"""
    state: str = Field(..., description="New state (running, waiting_for_input, completed, failed)")
    reasoning: str = Field(..., description="Reason for manual override")


@router.get("/{execution_id}/transitions")
async def get_execution_transitions(
    execution_id: str,
    organization: dict = Depends(get_current_organization),
):
    """
    Get transition history for an execution

    Returns all state transitions with AI reasoning for the specified execution.
    """
    try:
        client = get_supabase()

        # Verify execution belongs to organization
        exec_result = safe_execute_query(
            client.table("executions")
            .select("id")
            .eq("id", execution_id)
            .eq("organization_id", organization["id"])
        )

        if not exec_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Execution not found"
            )

        # Get all transitions for this execution
        transitions_result = safe_execute_query(
            client.table("execution_transitions")
            .select("*")
            .eq("execution_id", execution_id)
            .order("created_at", desc=False)
        )

        transitions = transitions_result if transitions_result else []

        logger.info(
            "execution_transitions_fetched",
            execution_id=execution_id,
            transition_count=len(transitions),
        )

        return {
            "execution_id": execution_id,
            "transition_count": len(transitions),
            "transitions": transitions,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "get_transitions_failed",
            execution_id=execution_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get transitions: {str(e)}"
        )


@router.post("/{execution_id}/transitions/override")
async def override_execution_state(
    execution_id: str,
    override: StateOverrideRequest,
    organization: dict = Depends(get_current_organization),
    request: Request = None,
):
    """
    Manually override execution state (admin/debug)

    Allows manual state transitions with reasoning. Records the override
    in the transitions table for audit purposes.
    """
    try:
        # Validate state
        valid_states = ["running", "waiting_for_input", "completed", "failed", "cancelled"]
        if override.state.lower() not in valid_states:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid state. Must be one of: {', '.join(valid_states)}"
            )

        client = get_supabase()

        # Verify execution belongs to organization
        exec_result = safe_execute_query(
            client.table("executions")
            .select("id, status")
            .eq("id", execution_id)
            .eq("organization_id", organization["id"])
        )

        if not exec_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Execution not found"
            )

        current_execution = exec_result[0]
        from_state = current_execution.get("status", "unknown")
        to_state = override.state.lower()

        # Update execution status
        update_data = {"status": to_state}

        if to_state in ["completed", "failed"]:
            update_data["completed_at"] = datetime.now(timezone.utc).isoformat()

        update_result = safe_execute_query(
            client.table("executions")
            .update(update_data)
            .eq("id", execution_id)
            .eq("organization_id", organization["id"])
        )

        if not update_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update execution status"
            )

        # Get user info from request headers or auth
        user_id = organization.get("user_id", "admin")
        override_user_email = organization.get("email", "unknown")

        # Record manual override in transitions table
        transition_record = {
            "organization_id": organization["id"],
            "execution_id": execution_id,
            "turn_number": 0,  # Manual overrides don't have a turn number
            "from_state": from_state,
            "to_state": to_state,
            "reasoning": f"MANUAL OVERRIDE by {override_user_email}: {override.reasoning}",
            "confidence": "high",  # Manual overrides are definitive
            "decision_factors": {
                "manual_override": True,
                "override_by": override_user_email,
                "override_user_id": user_id,
                "original_reasoning": override.reasoning,
            },
            "ai_model": "manual",
            "decision_time_ms": 0,
            "is_manual_override": True,
            "override_user_id": user_id,
            "override_reasoning": override.reasoning,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        transition_result = safe_execute_query(
            client.table("execution_transitions")
            .insert(transition_record)
        )

        logger.info(
            "execution_state_overridden",
            execution_id=execution_id,
            from_state=from_state,
            to_state=to_state,
            user=override_user_email,
            reasoning=override.reasoning[:100],
        )

        return {
            "success": True,
            "execution_id": execution_id,
            "from_state": from_state,
            "to_state": to_state,
            "override_by": override_user_email,
            "transition_id": transition_result[0]["id"] if transition_result else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "override_state_failed",
            execution_id=execution_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to override state: {str(e)}"
        )
