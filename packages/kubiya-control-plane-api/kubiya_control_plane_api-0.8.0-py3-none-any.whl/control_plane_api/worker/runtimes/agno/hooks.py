"""
Tool execution hooks for Agno runtime.

This module provides:
- Tool execution event hooks
- Real-time event publishing to Control Plane
- Event callback creation
- Tool execution tracking
- Policy enforcement for tool executions
"""

import uuid
import asyncio
import structlog
from typing import Callable, Any, Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from control_plane_client import ControlPlaneClient
    from control_plane_api.worker.services.tool_enforcement import ToolEnforcementService

logger = structlog.get_logger(__name__)


def create_tool_hook_for_streaming(
    control_plane: "ControlPlaneClient",
    execution_id: str,
    message_id: str,
    enforcement_context: Optional[Dict[str, Any]] = None,
    enforcement_service: Optional["ToolEnforcementService"] = None,
) -> Callable:
    """
    Create a tool hook for streaming execution that publishes directly to Control Plane.

    This hook publishes tool events immediately (not batched) for real-time visibility.
    Used in streaming execution mode. Includes policy enforcement checks.

    Args:
        control_plane: Control Plane client for publishing events
        execution_id: Execution ID for this run
        message_id: Message ID for the current assistant turn (links tool to conversation)
        enforcement_context: Optional context for policy enforcement
        enforcement_service: Optional enforcement service for policy checks

    Returns:
        Tool hook function for Agno agent
    """
    def tool_hook(
        name: str = None,
        function_name: str = None,
        function=None,
        arguments: dict = None,
        **kwargs,
    ):
        """Hook to capture tool execution for real-time streaming"""
        tool_name = name or function_name or "unknown"
        tool_args = arguments or {}
        # Use UUID for tool_execution_id to avoid collisions when tools run simultaneously
        tool_execution_id = f"{tool_name}_{uuid.uuid4().hex[:12]}"

        # Enforcement check (non-blocking)
        enforcement_allowed = True
        enforcement_violation = None
        enforcement_metadata = {}

        if enforcement_service and enforcement_context:
            try:
                # Run enforcement check asynchronously
                loop = asyncio.get_event_loop()
                enforcement_allowed, enforcement_violation, enforcement_metadata = (
                    loop.run_until_complete(
                        enforcement_service.enforce_tool_execution(
                            tool_name=tool_name,
                            tool_args=tool_args,
                            enforcement_context={
                                **enforcement_context,
                                "execution_id": execution_id,
                                "message_id": message_id,
                                "tool_execution_id": tool_execution_id,
                            },
                        )
                    )
                )
            except Exception as e:
                logger.error(
                    "enforcement_check_failed",
                    tool_name=tool_name,
                    error=str(e),
                )
                # Fail open - allow execution
                enforcement_metadata = {"enforcer": "error", "error": str(e)}

        # Publish tool start event (blocking call - OK in thread)
        control_plane.publish_event(
            execution_id=execution_id,
            event_type="tool_started",
            data={
                "tool_name": tool_name,
                "tool_execution_id": tool_execution_id,
                "tool_arguments": tool_args,
                "message_id": message_id,  # Link tool to assistant message
                "message": f"Executing tool: {tool_name}",
                "enforcement": enforcement_metadata,  # Add enforcement metadata
            }
        )

        # Execute tool (regardless of enforcement result - non-blocking approach)
        result = None
        error = None
        try:
            if function and callable(function):
                result = function(**tool_args) if tool_args else function()
            else:
                raise ValueError(f"Function not callable: {function}")
            status = "success"

            # Inject enforcement violation into result if blocked
            if not enforcement_allowed and enforcement_violation:
                # Prepend violation message to result
                violation_prefix = f"\n{'='*60}\n"
                violation_prefix += "⛔ POLICY VIOLATION DETECTED\n"
                violation_prefix += f"{'='*60}\n"
                violation_prefix += enforcement_violation
                violation_prefix += f"\n{'='*60}\n\n"

                if result:
                    result = violation_prefix + str(result)
                else:
                    result = violation_prefix + "(Tool execution completed but blocked by policy)"

                logger.warning(
                    "tool_execution_policy_violation",
                    tool_name=tool_name,
                    tool_execution_id=tool_execution_id,
                    enforcement_metadata=enforcement_metadata,
                )

        except Exception as e:
            error = e
            status = "failed"
            logger.error(
                "tool_execution_failed",
                tool_name=tool_name,
                error=str(e),
            )

        # Publish tool completion event with enforcement metadata
        control_plane.publish_event(
            execution_id=execution_id,
            event_type="tool_completed",
            data={
                "tool_name": tool_name,
                "tool_execution_id": tool_execution_id,
                "status": status,
                "tool_output": str(result)[:1000] if result else None,
                "tool_error": str(error) if error else None,
                "message_id": message_id,  # Link tool to assistant message
                "message": f"Tool {status}: {tool_name}",
                "enforcement": enforcement_metadata,  # Add enforcement metadata
            }
        )

        if error:
            raise error
        return result

    return tool_hook


def create_tool_hook_with_callback(
    execution_id: str,
    message_id: str,
    event_callback: Callable[[Dict[str, Any]], None],
    enforcement_context: Optional[Dict[str, Any]] = None,
    enforcement_service: Optional["ToolEnforcementService"] = None,
) -> Callable:
    """
    Create a tool hook that uses a callback for event publishing.

    This hook uses a callback function to publish events, allowing for flexible
    event handling (batching, filtering, etc.). Used in non-streaming execution.
    Includes policy enforcement checks.

    Args:
        execution_id: Execution ID for this run
        message_id: Message ID for the current assistant turn
        event_callback: Callback function for event publishing
        enforcement_context: Optional context for policy enforcement
        enforcement_service: Optional enforcement service for policy checks

    Returns:
        Tool hook function for Agno agent
    """
    def tool_hook(
        name: str = None,
        function_name: str = None,
        function=None,
        arguments: dict = None,
        **kwargs,
    ):
        """Hook to capture tool execution for real-time streaming"""
        tool_name = name or function_name or "unknown"
        tool_args = arguments or {}
        # Use UUID for tool_execution_id to avoid collisions
        tool_execution_id = f"{tool_name}_{uuid.uuid4().hex[:12]}"

        # Enforcement check (non-blocking)
        enforcement_allowed = True
        enforcement_violation = None
        enforcement_metadata = {}

        if enforcement_service and enforcement_context:
            try:
                # Run enforcement check asynchronously
                loop = asyncio.get_event_loop()
                enforcement_allowed, enforcement_violation, enforcement_metadata = (
                    loop.run_until_complete(
                        enforcement_service.enforce_tool_execution(
                            tool_name=tool_name,
                            tool_args=tool_args,
                            enforcement_context={
                                **enforcement_context,
                                "execution_id": execution_id,
                                "message_id": message_id,
                                "tool_execution_id": tool_execution_id,
                            },
                        )
                    )
                )
            except Exception as e:
                logger.error(
                    "enforcement_check_failed",
                    tool_name=tool_name,
                    error=str(e),
                )
                # Fail open - allow execution
                enforcement_metadata = {"enforcer": "error", "error": str(e)}

        # Publish tool start event via callback
        event_callback(
            {
                "type": "tool_start",
                "tool_name": tool_name,
                "tool_execution_id": tool_execution_id,
                "tool_args": tool_args,
                "message_id": message_id,
                "execution_id": execution_id,
                "enforcement": enforcement_metadata,  # Add enforcement metadata
            }
        )

        # Execute tool (regardless of enforcement result - non-blocking approach)
        result = None
        error = None
        try:
            if function and callable(function):
                result = function(**tool_args) if tool_args else function()
            else:
                raise ValueError(f"Function not callable: {function}")

            status = "success"

            # Inject enforcement violation into result if blocked
            if not enforcement_allowed and enforcement_violation:
                # Prepend violation message to result
                violation_prefix = f"\n{'='*60}\n"
                violation_prefix += "⛔ POLICY VIOLATION DETECTED\n"
                violation_prefix += f"{'='*60}\n"
                violation_prefix += enforcement_violation
                violation_prefix += f"\n{'='*60}\n\n"

                if result:
                    result = violation_prefix + str(result)
                else:
                    result = violation_prefix + "(Tool execution completed but blocked by policy)"

                logger.warning(
                    "tool_execution_policy_violation",
                    tool_name=tool_name,
                    tool_execution_id=tool_execution_id,
                    enforcement_metadata=enforcement_metadata,
                )

        except Exception as e:
            error = e
            status = "failed"
            logger.error(
                "tool_execution_failed",
                tool_name=tool_name,
                error=str(e),
            )

        # Publish tool completion event via callback with enforcement metadata
        event_callback(
            {
                "type": "tool_complete",
                "tool_name": tool_name,
                "tool_execution_id": tool_execution_id,
                "status": status,
                "output": str(result)[:1000] if result else None,
                "error": str(error) if error else None,
                "message_id": message_id,
                "execution_id": execution_id,
                "enforcement": enforcement_metadata,  # Add enforcement metadata
            }
        )

        if error:
            raise error

        return result

    return tool_hook
