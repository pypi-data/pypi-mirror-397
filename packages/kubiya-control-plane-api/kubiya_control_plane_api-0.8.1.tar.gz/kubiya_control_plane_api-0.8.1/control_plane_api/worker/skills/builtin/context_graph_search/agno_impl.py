"""Context Graph Search skill implementation for all runtimes."""
import os
import json
import structlog
from typing import Optional, Dict, Any, List
import httpx
from agno.tools import Toolkit

logger = structlog.get_logger(__name__)


class ContextGraphSearchTools(Toolkit):
    """
    Context Graph Search toolkit for querying Neo4j-based context graphs.

    Provides tools for:
    - Searching nodes by properties
    - Getting node details and relationships
    - Traversing subgraphs
    - Text-based search
    - Executing custom Cypher queries
    - Getting graph metadata (labels, types, stats)
    """

    def __init__(
        self,
        api_base: Optional[str] = None,
        timeout: int = 30,
        default_limit: int = 100,
        **kwargs
    ):
        """
        Initialize Context Graph Search tools.

        Args:
            api_base: Context Graph API base URL (defaults to CONTEXT_GRAPH_API_BASE env var)
            timeout: Request timeout in seconds
            default_limit: Default result limit for queries
            **kwargs: Additional configuration
        """
        super().__init__(name="context-graph-search")

        # Get configuration from params or environment
        self.api_base = (api_base or
                        os.environ.get("CONTEXT_GRAPH_API_BASE",
                                     "https://graph.kubiya.ai")).rstrip("/")
        self.timeout = timeout
        self.default_limit = default_limit

        # Get authentication
        self.api_key = os.environ.get("KUBIYA_API_KEY")
        self.org_id = os.environ.get("KUBIYA_ORG_ID")

        if not self.api_key:
            logger.warning("No KUBIYA_API_KEY provided - context graph queries will fail")

        # Prepare headers
        self.headers = {
            "Authorization": f"UserKey {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Kubiya-Client": "agent-runtime-builtin-tool",
        }

        if self.org_id:
            self.headers["X-Organization-ID"] = self.org_id

        # Register all tool methods
        self.register(self.search_nodes)
        self.register(self.get_node)
        self.register(self.get_relationships)
        self.register(self.get_subgraph)
        self.register(self.search_by_text)
        self.register(self.execute_query)
        self.register(self.get_labels)
        self.register(self.get_relationship_types)
        self.register(self.get_stats)

        logger.info(f"Initialized Context Graph Search tools (api_base: {self.api_base})")

    def _make_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Context Graph API.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path (e.g., "/api/v1/graph/nodes")
            params: Query parameters
            body: Request body for POST requests

        Returns:
            Response JSON

        Raises:
            Exception: If request fails
        """
        url = f"{self.api_base}{path}"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                if method == "GET":
                    response = client.get(url, headers=self.headers, params=params)
                elif method == "POST":
                    response = client.post(url, headers=self.headers, params=params, json=body)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException:
            raise Exception(f"Request timed out after {self.timeout}s: {method} {path}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    def search_nodes(
        self,
        label: Optional[str] = None,
        property_name: Optional[str] = None,
        property_value: Optional[str] = None,
        integration: Optional[str] = None,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> str:
        """
        Search for nodes in the context graph by label and/or properties.

        Args:
            label: Node label to filter by (e.g., "User", "Repository", "Service")
            property_name: Property name to filter by
            property_value: Property value to match
            integration: Integration name to filter by
            skip: Number of results to skip
            limit: Maximum number of results to return

        Returns:
            JSON string with search results

        Example:
            search_nodes(label="User", property_name="email", property_value="user@example.com")
            search_nodes(label="Repository", integration="github")
        """
        body = {}
        if label:
            body["label"] = label
        if property_name:
            body["property_name"] = property_name
        if property_value:
            body["property_value"] = property_value

        params = {
            "skip": skip,
            "limit": limit or self.default_limit,
        }
        if integration:
            params["integration"] = integration

        result = self._make_request("POST", "/api/v1/graph/nodes/search", params=params, body=body)
        return json.dumps(result, indent=2)

    def get_node(
        self,
        node_id: str,
        integration: Optional[str] = None,
    ) -> str:
        """
        Get a specific node by its ID.

        Args:
            node_id: The node ID to retrieve
            integration: Optional integration name to filter by

        Returns:
            JSON string with node details

        Example:
            get_node(node_id="abc123")
        """
        params = {}
        if integration:
            params["integration"] = integration

        result = self._make_request("GET", f"/api/v1/graph/nodes/{node_id}", params=params)
        return json.dumps(result, indent=2)

    def get_relationships(
        self,
        node_id: str,
        direction: str = "both",
        relationship_type: Optional[str] = None,
        integration: Optional[str] = None,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> str:
        """
        Get relationships for a specific node.

        Args:
            node_id: The node ID to get relationships for
            direction: Relationship direction ("incoming", "outgoing", or "both")
            relationship_type: Optional relationship type to filter by
            integration: Optional integration name to filter by
            skip: Number of results to skip
            limit: Maximum number of results to return

        Returns:
            JSON string with relationships

        Example:
            get_relationships(node_id="abc123", direction="outgoing", relationship_type="OWNS")
        """
        params = {
            "direction": direction,
            "skip": skip,
            "limit": limit or self.default_limit,
        }
        if relationship_type:
            params["relationship_type"] = relationship_type
        if integration:
            params["integration"] = integration

        result = self._make_request("GET", f"/api/v1/graph/nodes/{node_id}/relationships", params=params)
        return json.dumps(result, indent=2)

    def get_subgraph(
        self,
        node_id: str,
        depth: int = 1,
        relationship_types: Optional[List[str]] = None,
        integration: Optional[str] = None,
    ) -> str:
        """
        Get a subgraph starting from a node.

        Args:
            node_id: Starting node ID
            depth: Traversal depth (1-5)
            relationship_types: Optional list of relationship types to follow
            integration: Optional integration name to filter by

        Returns:
            JSON string with subgraph (nodes and relationships)

        Example:
            get_subgraph(node_id="abc123", depth=2, relationship_types=["OWNS", "MANAGES"])
        """
        body = {
            "node_id": node_id,
            "depth": min(max(depth, 1), 5),  # Clamp between 1 and 5
        }
        if relationship_types:
            body["relationship_types"] = relationship_types

        params = {}
        if integration:
            params["integration"] = integration

        result = self._make_request("POST", "/api/v1/graph/subgraph", params=params, body=body)
        return json.dumps(result, indent=2)

    def search_by_text(
        self,
        property_name: str,
        search_text: str,
        label: Optional[str] = None,
        integration: Optional[str] = None,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> str:
        """
        Search nodes by text pattern in a property.

        Args:
            property_name: Property name to search in
            search_text: Text to search for (supports partial matching)
            label: Optional node label to filter by
            integration: Optional integration name to filter by
            skip: Number of results to skip
            limit: Maximum number of results to return

        Returns:
            JSON string with search results

        Example:
            search_by_text(property_name="name", search_text="kubernetes", label="Service")
        """
        body = {
            "property_name": property_name,
            "search_text": search_text,
        }
        if label:
            body["label"] = label

        params = {
            "skip": skip,
            "limit": limit or self.default_limit,
        }
        if integration:
            params["integration"] = integration

        result = self._make_request("POST", "/api/v1/graph/nodes/search/text", params=params, body=body)
        return json.dumps(result, indent=2)

    def execute_query(
        self,
        query: str,
    ) -> str:
        """
        Execute a custom Cypher query (read-only).

        The query will be automatically scoped to your organization's data.
        All node patterns will have the organization label injected.

        Args:
            query: Cypher query to execute (read-only)

        Returns:
            JSON string with query results

        Example:
            execute_query(query="MATCH (u:User)-[:OWNS]->(r:Repository) RETURN u.name, r.name LIMIT 10")
        """
        body = {"query": query}

        result = self._make_request("POST", "/api/v1/graph/query", body=body)
        return json.dumps(result, indent=2)

    def get_labels(
        self,
        integration: Optional[str] = None,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> str:
        """
        Get all node labels in the context graph.

        Args:
            integration: Optional integration name to filter by
            skip: Number of results to skip
            limit: Maximum number of results to return

        Returns:
            JSON string with available labels

        Example:
            get_labels()
            get_labels(integration="github")
        """
        params = {
            "skip": skip,
            "limit": limit or self.default_limit,
        }
        if integration:
            params["integration"] = integration

        result = self._make_request("GET", "/api/v1/graph/labels", params=params)
        return json.dumps(result, indent=2)

    def get_relationship_types(
        self,
        integration: Optional[str] = None,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> str:
        """
        Get all relationship types in the context graph.

        Args:
            integration: Optional integration name to filter by
            skip: Number of results to skip
            limit: Maximum number of results to return

        Returns:
            JSON string with available relationship types

        Example:
            get_relationship_types()
            get_relationship_types(integration="github")
        """
        params = {
            "skip": skip,
            "limit": limit or self.default_limit,
        }
        if integration:
            params["integration"] = integration

        result = self._make_request("GET", "/api/v1/graph/relationship-types", params=params)
        return json.dumps(result, indent=2)

    def get_stats(
        self,
        integration: Optional[str] = None,
    ) -> str:
        """
        Get statistics about the context graph.

        Args:
            integration: Optional integration name to filter by

        Returns:
            JSON string with graph statistics (node counts, relationship counts, etc.)

        Example:
            get_stats()
            get_stats(integration="github")
        """
        params = {}
        if integration:
            params["integration"] = integration

        result = self._make_request("GET", "/api/v1/graph/stats", params=params)
        return json.dumps(result, indent=2)
