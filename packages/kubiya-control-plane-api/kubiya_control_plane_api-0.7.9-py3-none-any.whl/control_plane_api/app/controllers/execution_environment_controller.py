"""
Execution Environment Controller - Centralized logic for resolving execution environments

This controller provides reusable logic for resolving execution environments for agents/teams.
It can be called from:
- API routes (for HTTP requests)
- Workers (for direct execution)
- Other internal services

The controller handles:
- Fetching execution environment configs from database
- Resolving secret names to actual values from Kubiya API
- Resolving integration IDs to actual tokens from Kubiya API
- Merging configs from environments + agent/team
- Template resolution in config fields
"""

import httpx
from typing import Dict, Any, List
from sqlalchemy.orm import Session
import structlog

from control_plane_api.app.models import (
    Agent,
    Team,
    Environment,
    AgentEnvironment,
    TeamEnvironment,
)
from control_plane_api.app.lib.kubiya_client import KUBIYA_API_BASE
from control_plane_api.app.lib.templating import TemplateContext, resolve_templates

logger = structlog.get_logger(__name__)


# Integration type to environment variable name mapping
INTEGRATION_ENV_VAR_MAP = {
    "github": "GH_TOKEN",
    "github_app": "GITHUB_TOKEN",
    "jira": "JIRA_TOKEN",
    "slack": "SLACK_TOKEN",
    "aws": "AWS_ACCESS_KEY_ID",
    "aws-serviceaccount": "AWS_ROLE_ARN",
    "kubernetes": "KUBECONFIG",
}


class ExecutionEnvironmentResolutionError(Exception):
    """Raised when execution environment resolution fails"""
    pass


async def resolve_secret_value(
    secret_name: str,
    token: str,
    org_id: str,
) -> str:
    """
    Resolve a secret name to its actual value from Kubiya API.

    Args:
        secret_name: Name of the secret to resolve
        token: Kubiya API token
        org_id: Organization ID

    Returns:
        Secret value as string

    Raises:
        ExecutionEnvironmentResolutionError: If secret resolution fails
    """
    headers = {
        "Authorization": f"UserKey {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Kubiya-Client": "agent-control-plane",
        "X-Organization-ID": org_id,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{KUBIYA_API_BASE}/api/v2/secrets/get_value/{secret_name}",
            headers=headers,
        )

        if response.status_code == 200:
            return response.text
        else:
            logger.warning(
                "secret_resolution_failed",
                secret_name=secret_name[:20],
                status=response.status_code,
            )
            raise ExecutionEnvironmentResolutionError(
                f"Failed to resolve secret '{secret_name}': {response.text[:200]}"
            )


async def resolve_integration_token(
    integration_id: str,
    integration_type: str,
    token: str,
    org_id: str,
) -> Dict[str, str]:
    """
    Resolve an integration ID to its actual token from Kubiya API.

    Args:
        integration_id: Integration UUID
        integration_type: Type of integration (github, jira, etc.)
        token: Kubiya API token
        org_id: Organization ID

    Returns:
        Dict with env_var_name and token value
    """
    headers = {
        "Authorization": f"UserKey {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Kubiya-Client": "agent-control-plane",
        "X-Organization-ID": org_id,
    }

    # Build token URL based on integration type
    integration_type_lower = integration_type.lower()

    if integration_type_lower == "github":
        token_url = f"{KUBIYA_API_BASE}/api/v1/integration/github/token/{integration_id}"
    elif integration_type_lower == "github_app":
        token_url = f"{KUBIYA_API_BASE}/api/v1/integration/github_app/token/{integration_id}"
    elif integration_type_lower == "jira":
        token_url = f"{KUBIYA_API_BASE}/api/v1/integration/jira/token/{integration_id}"
    else:
        logger.warning(
            "unsupported_integration_type",
            integration_type=integration_type,
            integration_id=integration_id[:8],
        )
        # For unsupported types, skip
        return {}

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(token_url, headers=headers)

        if response.status_code == 200:
            # Try to parse as JSON first
            try:
                token_data = response.json()
                token_value = token_data.get("token", response.text)
            except:
                # If not JSON, use plain text
                token_value = response.text

            # Map to env var name
            env_var_name = INTEGRATION_ENV_VAR_MAP.get(
                integration_type_lower, f"{integration_type.upper()}_TOKEN"
            )

            return {env_var_name: token_value}
        else:
            logger.warning(
                "integration_token_resolution_failed",
                integration_id=integration_id[:8],
                integration_type=integration_type,
                status=response.status_code,
            )
            # Don't fail the entire request for one integration
            return {}


async def resolve_environment_configs(
    environment_ids: List[str],
    org_id: str,
    db: Session,
) -> Dict[str, Any]:
    """
    Resolve execution environment configs from a list of environment IDs.
    Merges configs from all environments.

    Args:
        environment_ids: List of environment IDs
        org_id: Organization ID
        db: Database session

    Returns:
        Merged execution environment dict with env_vars, secrets, integration_ids, mcp_servers
    """
    if not environment_ids:
        return {
            "env_vars": {},
            "secrets": [],
            "integration_ids": [],
            "mcp_servers": {},
        }

    # Fetch all environments
    environments = (
        db.query(Environment)
        .filter(Environment.id.in_(environment_ids), Environment.organization_id == org_id)
        .all()
    )

    # Merge all environment configs
    merged_env_vars = {}
    merged_secrets = set()
    merged_integration_ids = set()
    merged_mcp_servers = {}

    for env in environments:
        env_config = env.execution_environment or {}

        # Merge env vars (later environments override earlier ones)
        merged_env_vars.update(env_config.get("env_vars", {}))

        # Collect secrets (union)
        merged_secrets.update(env_config.get("secrets", []))

        # Collect integration IDs (union)
        merged_integration_ids.update(env_config.get("integration_ids", []))

        # Merge MCP servers (later environments override earlier ones)
        merged_mcp_servers.update(env_config.get("mcp_servers", {}))

    return {
        "env_vars": merged_env_vars,
        "secrets": list(merged_secrets),
        "integration_ids": list(merged_integration_ids),
        "mcp_servers": merged_mcp_servers,
    }


def apply_template_resolution(
    config: Dict[str, Any],
    resolved_secrets: Dict[str, str],
    resolved_env_vars: Dict[str, str],
) -> Dict[str, Any]:
    """
    Apply template resolution to a configuration object.

    Resolves all templates in the config using resolved secrets and env vars.
    Templates are resolved recursively in all string fields.

    Args:
        config: Configuration dict with potential templates
        resolved_secrets: Map of secret names to resolved values
        resolved_env_vars: Map of env var names to values

    Returns:
        Configuration with all templates resolved
    """
    try:
        # Build template context
        context = TemplateContext(
            variables={},
            secrets=resolved_secrets,
            env_vars=resolved_env_vars,
        )

        # Apply template resolution recursively to entire config
        resolved_config = resolve_templates(config, context, skip_on_error=True)

        logger.debug(
            "template_resolution_applied",
            config_keys=list(config.keys()),
            secrets_count=len(resolved_secrets),
            env_vars_count=len(resolved_env_vars),
        )

        return resolved_config

    except Exception as e:
        logger.error(
            "template_resolution_failed",
            error=str(e),
            config_keys=list(config.keys()),
        )
        # Return original config on error to avoid breaking execution
        return config


async def resolve_agent_execution_environment(
    agent_id: str,
    org_id: str,
    db: Session,
    kubiya_token: str = None,
) -> Dict[str, Any]:
    """
    Resolve complete execution environment for an agent.

    This is the main controller function that:
    1. Fetches agent config and associated environments from database
    2. Merges environment configs (env vars, secrets, integrations, MCP servers)
    3. Resolves secret names to actual values from Kubiya API
    4. Resolves integration IDs to actual tokens from Kubiya API
    5. Applies template resolution to all config fields
    6. Returns complete resolved execution environment

    Args:
        agent_id: Agent UUID
        org_id: Organization ID
        db: Database session
        kubiya_token: Kubiya API token for secret/integration resolution (optional, uses env var if not provided)

    Returns:
        Dict with:
        - env_vars: Resolved environment variables (dict)
        - mcp_servers: MCP server configs with templates resolved (dict)
        - system_prompt: Resolved system prompt (str)
        - description: Resolved description (str)
        - configuration: Resolved agent configuration (dict)

    Raises:
        ExecutionEnvironmentResolutionError: If agent not found or resolution fails
    """
    try:
        # Use environment KUBIYA_API_KEY if token not provided
        # This is needed because the JWT bearer token from requests doesn't work with Kubiya secrets API
        import os
        if not kubiya_token:
            kubiya_token = os.environ.get("KUBIYA_API_KEY")
            if not kubiya_token:
                logger.warning(
                    "kubiya_api_key_not_available",
                    agent_id=agent_id[:8],
                    note="Secrets and integrations will not be resolved"
                )
                # Continue without secret resolution
        # Fetch agent with configuration fields
        agent = (
            db.query(Agent)
            .filter(Agent.id == agent_id, Agent.organization_id == org_id)
            .first()
        )

        if not agent:
            raise ExecutionEnvironmentResolutionError(
                f"Agent {agent_id} not found in organization {org_id}"
            )

        # Get environment associations from join table
        env_associations = (
            db.query(AgentEnvironment)
            .filter(AgentEnvironment.agent_id == agent_id)
            .all()
        )
        environment_ids = [str(assoc.environment_id) for assoc in env_associations]

        # Resolve and merge environment configs
        env_config = await resolve_environment_configs(environment_ids, org_id, db)

        # Get agent-level config
        agent_exec_env = agent.execution_environment or {}
        agent_configuration = agent.configuration or {}

        # Merge: environment config + agent config (agent overrides environment)
        execution_environment = {
            "env_vars": {
                **env_config.get("env_vars", {}),
                **agent_exec_env.get("env_vars", {}),
            },
            "secrets": list(
                set(env_config.get("secrets", []) + agent_exec_env.get("secrets", []))
            ),
            "integration_ids": list(
                set(
                    env_config.get("integration_ids", [])
                    + agent_exec_env.get("integration_ids", [])
                )
            ),
            "mcp_servers": {
                **env_config.get("mcp_servers", {}),
                **agent_exec_env.get("mcp_servers", {}),
            },
        }

        # Start with custom env vars
        resolved_env_vars = dict(execution_environment.get("env_vars", {}))
        resolved_secrets = {}

        # Add KUBIYA_API_KEY to resolved_env_vars for template resolution
        # This allows MCP server configs to use {{KUBIYA_API_KEY}} templates
        import os
        kubiya_api_key_from_env = os.environ.get("KUBIYA_API_KEY")
        if kubiya_api_key_from_env:
            resolved_env_vars["KUBIYA_API_KEY"] = kubiya_api_key_from_env

        # Resolve secrets
        secrets = execution_environment.get("secrets", [])
        for secret_name in secrets:
            try:
                secret_value = await resolve_secret_value(
                    secret_name, kubiya_token, org_id
                )
                resolved_env_vars[secret_name] = secret_value
                resolved_secrets[secret_name] = secret_value
                logger.debug(
                    "secret_resolved",
                    agent_id=agent_id[:8],
                    secret_name=secret_name[:20],
                )
            except Exception as e:
                logger.error(
                    "secret_resolution_error",
                    agent_id=agent_id[:8],
                    secret_name=secret_name[:20],
                    error=str(e),
                )
                # Continue with other secrets even if one fails

        # Resolve integrations
        integration_ids = execution_environment.get("integration_ids", [])
        if integration_ids:
            headers = {
                "Authorization": f"UserKey {kubiya_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-Kubiya-Client": "agent-control-plane",
                "X-Organization-ID": org_id,
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{KUBIYA_API_BASE}/api/v2/integrations?full=true",
                    headers=headers,
                )

                if response.status_code == 200:
                    all_integrations = response.json()

                    for integration_id in integration_ids:
                        integration = next(
                            (
                                i
                                for i in all_integrations
                                if i.get("uuid") == integration_id
                            ),
                            None,
                        )

                        if integration:
                            integration_type = integration.get("integration_type", "")
                            try:
                                token_env_vars = await resolve_integration_token(
                                    integration_id,
                                    integration_type,
                                    kubiya_token,
                                    org_id,
                                )
                                resolved_env_vars.update(token_env_vars)
                                logger.debug(
                                    "integration_resolved",
                                    agent_id=agent_id[:8],
                                    integration_id=integration_id[:8],
                                    integration_type=integration_type,
                                )
                            except Exception as e:
                                logger.error(
                                    "integration_resolution_error",
                                    agent_id=agent_id[:8],
                                    integration_id=integration_id[:8],
                                    error=str(e),
                                )

        # Build complete config to resolve templates
        complete_config = {
            "system_prompt": agent_configuration.get("system_prompt"),
            "description": agent.description,
            "configuration": agent_configuration,
            "mcp_servers": execution_environment.get("mcp_servers", {}),
            "env_vars": execution_environment.get("env_vars", {}),
        }

        # Apply template resolution to ENTIRE config
        resolved_config = apply_template_resolution(
            complete_config, resolved_secrets, resolved_env_vars
        )

        mcp_servers_resolved = resolved_config.get("mcp_servers", {})

        logger.info(
            "agent_execution_environment_resolved",
            agent_id=agent_id[:8],
            env_var_count=len(resolved_env_vars),
            mcp_server_count=len(mcp_servers_resolved),
            mcp_server_names=list(mcp_servers_resolved.keys()),
            secrets_count=len(resolved_secrets),
        )

        return {
            "env_vars": resolved_env_vars,
            "mcp_servers": mcp_servers_resolved,
            "system_prompt": resolved_config.get("system_prompt"),
            "description": resolved_config.get("description"),
            "configuration": resolved_config.get("configuration", {}),
        }

    except ExecutionEnvironmentResolutionError:
        raise
    except Exception as e:
        logger.error(
            "agent_execution_environment_resolution_error",
            agent_id=agent_id[:8],
            error=str(e),
            exc_info=True,
        )
        raise ExecutionEnvironmentResolutionError(
            f"Failed to resolve execution environment for agent {agent_id}: {str(e)}"
        )


async def resolve_team_execution_environment(
    team_id: str,
    org_id: str,
    db: Session,
    kubiya_token: str = None,
) -> Dict[str, Any]:
    """
    Resolve complete execution environment for a team.

    Similar to resolve_agent_execution_environment but for teams.

    Args:
        team_id: Team UUID
        org_id: Organization ID
        db: Database session
        kubiya_token: Kubiya API token for secret/integration resolution (optional, uses env var if not provided)

    Returns:
        Dict with resolved execution environment

    Raises:
        ExecutionEnvironmentResolutionError: If team not found or resolution fails
    """
    try:
        # Use environment KUBIYA_API_KEY if token not provided
        import os
        if not kubiya_token:
            kubiya_token = os.environ.get("KUBIYA_API_KEY")
            if not kubiya_token:
                logger.warning(
                    "kubiya_api_key_not_available",
                    team_id=team_id[:8],
                    note="Secrets and integrations will not be resolved"
                )
        # Fetch team with configuration fields
        team = (
            db.query(Team)
            .filter(Team.id == team_id, Team.organization_id == org_id)
            .first()
        )

        if not team:
            raise ExecutionEnvironmentResolutionError(
                f"Team {team_id} not found in organization {org_id}"
            )

        # Get environment-level configs
        environment_ids = team.environment_ids or []
        env_config = await resolve_environment_configs(environment_ids, org_id, db)

        # Get team-level config
        team_exec_env = team.execution_environment or {}

        # Merge: environment config + team config (team overrides environment)
        execution_environment = {
            "env_vars": {
                **env_config.get("env_vars", {}),
                **team_exec_env.get("env_vars", {}),
            },
            "secrets": list(
                set(env_config.get("secrets", []) + team_exec_env.get("secrets", []))
            ),
            "integration_ids": list(
                set(
                    env_config.get("integration_ids", [])
                    + team_exec_env.get("integration_ids", [])
                )
            ),
            "mcp_servers": {
                **env_config.get("mcp_servers", {}),
                **team_exec_env.get("mcp_servers", {}),
            },
        }

        # Start with custom env vars
        resolved_env_vars = dict(execution_environment.get("env_vars", {}))
        resolved_secrets = {}

        # Add KUBIYA_API_KEY to resolved_env_vars for template resolution
        # This allows MCP server configs to use {{KUBIYA_API_KEY}} templates
        kubiya_api_key_from_env = os.environ.get("KUBIYA_API_KEY")
        if kubiya_api_key_from_env:
            resolved_env_vars["KUBIYA_API_KEY"] = kubiya_api_key_from_env

        # Resolve secrets
        secrets = execution_environment.get("secrets", [])
        for secret_name in secrets:
            try:
                secret_value = await resolve_secret_value(
                    secret_name, kubiya_token, org_id
                )
                resolved_env_vars[secret_name] = secret_value
                resolved_secrets[secret_name] = secret_value
                logger.debug(
                    "secret_resolved",
                    team_id=team_id[:8],
                    secret_name=secret_name[:20],
                )
            except Exception as e:
                logger.error(
                    "secret_resolution_error",
                    team_id=team_id[:8],
                    secret_name=secret_name[:20],
                    error=str(e),
                )

        # Resolve integrations
        integration_ids = execution_environment.get("integration_ids", [])
        if integration_ids:
            headers = {
                "Authorization": f"UserKey {kubiya_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-Kubiya-Client": "agent-control-plane",
                "X-Organization-ID": org_id,
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{KUBIYA_API_BASE}/api/v2/integrations?full=true",
                    headers=headers,
                )

                if response.status_code == 200:
                    all_integrations = response.json()

                    for integration_id in integration_ids:
                        integration = next(
                            (
                                i
                                for i in all_integrations
                                if i.get("uuid") == integration_id
                            ),
                            None,
                        )

                        if integration:
                            integration_type = integration.get("integration_type", "")
                            try:
                                token_env_vars = await resolve_integration_token(
                                    integration_id,
                                    integration_type,
                                    kubiya_token,
                                    org_id,
                                )
                                resolved_env_vars.update(token_env_vars)
                                logger.debug(
                                    "integration_resolved",
                                    team_id=team_id[:8],
                                    integration_id=integration_id[:8],
                                    integration_type=integration_type,
                                )
                            except Exception as e:
                                logger.error(
                                    "integration_resolution_error",
                                    team_id=team_id[:8],
                                    integration_id=integration_id[:8],
                                    error=str(e),
                                )

        # Build complete config to resolve templates
        complete_config = {
            "instructions": (
                team.configuration.get("instructions") if team.configuration else None
            ),
            "description": team.description,
            "configuration": team.configuration or {},
            "mcp_servers": execution_environment.get("mcp_servers", {}),
            "env_vars": execution_environment.get("env_vars", {}),
        }

        # Apply template resolution to ENTIRE config
        resolved_config = apply_template_resolution(
            complete_config, resolved_secrets, resolved_env_vars
        )

        logger.info(
            "team_execution_environment_resolved",
            team_id=team_id[:8],
            env_var_count=len(resolved_env_vars),
            mcp_server_count=len(resolved_config.get("mcp_servers", {})),
            secrets_count=len(resolved_secrets),
        )

        return {
            "env_vars": resolved_env_vars,
            "mcp_servers": resolved_config.get("mcp_servers", {}),
            "instructions": resolved_config.get("instructions"),
            "description": resolved_config.get("description"),
            "configuration": resolved_config.get("configuration", {}),
        }

    except ExecutionEnvironmentResolutionError:
        raise
    except Exception as e:
        logger.error(
            "team_execution_environment_resolution_error",
            team_id=team_id[:8],
            error=str(e),
            exc_info=True,
        )
        raise ExecutionEnvironmentResolutionError(
            f"Failed to resolve execution environment for team {team_id}: {str(e)}"
        )
