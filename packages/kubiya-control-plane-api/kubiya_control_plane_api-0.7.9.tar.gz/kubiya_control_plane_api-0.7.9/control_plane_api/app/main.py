from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

from control_plane_api.app.config import settings
from control_plane_api.app.routers import agents, teams, workflows, health, executions, presence, runners, workers, projects, models, models_v2, task_queues, worker_queues, environment_context, team_context, context_manager, skills, skills_definitions, environments, runtimes, secrets, integrations, execution_environment, policies, task_planning, jobs, analytics, context_graph, templates, enforcer, auth, storage, client_config
from control_plane_api.app.routers import agents_v2  # New multi-tenant agent router

# Configure structured logging
import logging

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(
        getattr(logging, settings.log_level.upper(), logging.INFO)
    ),
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info(
        "agent_control_plane_starting",
        version=settings.api_version,
        environment=settings.environment
    )
    # No database initialization needed for serverless
    # Supabase client is initialized on-demand

    # Initialize event bus if configured
    event_bus_manager = None
    if hasattr(settings, 'event_bus') and settings.event_bus:
        try:
            from control_plane_api.app.lib.event_bus.manager import EventBusManager, EventBusManagerConfig

            manager_config = EventBusManagerConfig(**settings.event_bus)
            event_bus_manager = EventBusManager(manager_config)
            await event_bus_manager.initialize()

            # Store in app state for access by routes
            app.state.event_bus = event_bus_manager

            logger.info(
                "event_bus_initialized",
                providers=event_bus_manager.get_provider_names(),
                count=len(event_bus_manager.providers)
            )
        except ImportError as e:
            logger.warning(
                "event_bus_dependencies_missing",
                error=str(e),
                message="Install event bus dependencies with: pip install kubiya-control-plane-api[event-bus]"
            )
        except Exception as e:
            logger.error(
                "event_bus_initialization_failed",
                error=str(e),
                message="Event bus will not be available"
            )

    yield

    # Shutdown event bus
    if event_bus_manager:
        try:
            await event_bus_manager.shutdown()
            logger.info("event_bus_shutdown")
        except Exception as e:
            logger.error("event_bus_shutdown_failed", error=str(e))

    logger.info("agent_control_plane_shutting_down")


# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan,
    # Disable lifespan for Vercel (will be "off" via Mangum)
    openapi_url="/api/openapi.json" if settings.environment != "production" else None,
    docs_url="/api/docs" if settings.environment != "production" else None,
    redoc_url="/api/redoc" if settings.environment != "production" else None,
    # Configure OpenAPI security scheme for Swagger UI
    swagger_ui_parameters={
        "persistAuthorization": True,  # Remember auth token across page refreshes
    },
)

# Configure security scheme for OpenAPI/Swagger
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.api_title,
        version=settings.api_version,
        description=settings.api_description,
        routes=app.routes,
    )

    # Add security scheme for Bearer token
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your Kubiya API token (format: Bearer <token>)",
        }
    }

    # Apply security globally to all endpoints
    openapi_schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (all routes under /api/v1)
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(auth.router, tags=["Authentication"])  # Auth validation for delegated auth from other services
app.include_router(client_config.router, prefix="/api/v1", tags=["Client Config"])  # Client configuration for service discovery
app.include_router(models_v2.router, prefix="/api/v1/models", tags=["Models"])  # LLM models CRUD (database-backed)
app.include_router(runtimes.router, prefix="/api/v1", tags=["Runtimes"])  # Agent runtime types
app.include_router(secrets.router, prefix="/api/v1", tags=["Secrets"])  # Kubiya secrets proxy
app.include_router(integrations.router, prefix="/api/v1", tags=["Integrations"])  # Kubiya integrations proxy
app.include_router(context_graph.router, prefix="/api/v1", tags=["Context Graph"])  # Context Graph API proxy
app.include_router(templates.router, prefix="/api/v1", tags=["Templates"])  # Template compilation and validation
app.include_router(execution_environment.router, prefix="/api/v1", tags=["Execution Environment"])  # Resolved execution environment for workers
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])  # Multi-project management
app.include_router(environments.router, prefix="/api/v1/environments", tags=["Environments"])  # Environment management
app.include_router(task_queues.router, prefix="/api/v1/task-queues", tags=["Task Queues"])  # Legacy endpoint (use /environments)
app.include_router(worker_queues.router, prefix="/api/v1", tags=["Worker Queues"])  # Worker queue management per environment
app.include_router(environment_context.router, prefix="/api/v1", tags=["Environment Context"])  # Environment context management
app.include_router(team_context.router, prefix="/api/v1", tags=["Team Context"])  # Team context management
app.include_router(context_manager.router, prefix="/api/v1", tags=["Context Manager"])  # Unified context management
app.include_router(skills_definitions.router, prefix="/api/v1/skills", tags=["Tool Sets"])  # Skill definitions and templates (must be before skills.router)
app.include_router(skills.router, prefix="/api/v1/skills", tags=["Tool Sets"])  # Tool sets management
app.include_router(enforcer.router, prefix="/api/v1", tags=["Enforcer"])  # OPA Watchdog enforcer proxy
app.include_router(policies.router, prefix="/api/v1/policies", tags=["Policies"])  # Policy management and enforcement
app.include_router(task_planning.router, prefix="/api/v1", tags=["Task Planning"])  # AI-powered task planning
app.include_router(agents_v2.router, prefix="/api/v1/agents", tags=["Agents"])  # Use new multi-tenant router
app.include_router(runners.router, prefix="/api/v1/runners", tags=["Runners"])  # Proxy to Kubiya API
app.include_router(workers.router, prefix="/api/v1/workers", tags=["Workers"])  # Worker registration and heartbeats
app.include_router(teams.router, prefix="/api/v1/teams", tags=["Teams"])
app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["Workflows"])
app.include_router(executions.router, prefix="/api/v1/executions", tags=["Executions"])
app.include_router(presence.router, prefix="/api/v1/presence", tags=["Presence"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])  # Scheduled and webhook-triggered jobs
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])  # Execution metrics and reporting
app.include_router(storage.router, prefix="/api/v1/storage", tags=["Storage"])  # Remote filesystem and cloud storage


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Agent Control Plane",
        "version": settings.api_version,
        "environment": settings.environment,
        "docs": "/api/docs" if settings.environment != "production" else None,
    }


@app.get("/api")
async def api_root():
    """API root endpoint"""
    return {
        "message": "Agent Control Plane API",
        "version": settings.api_version,
        "endpoints": {
            "projects": "/api/v1/projects",
            "task_queues": "/api/v1/task-queues",
            "agents": "/api/v1/agents",
            "teams": "/api/v1/teams",
            "skills": "/api/v1/skills",
            "policies": "/api/v1/policies",
            "workflows": "/api/v1/workflows",
            "executions": "/api/v1/executions",
            "presence": "/api/v1/presence",
            "runners": "/api/v1/runners",
            "workers": "/api/v1/workers",
            "models": "/api/v1/models",
            "runtimes": "/api/v1/runtimes",
            "secrets": "/api/v1/secrets",
            "integrations": "/api/v1/integrations",
            "context_graph": "/api/v1/context-graph",
            "health": "/api/health",
        }
    }
