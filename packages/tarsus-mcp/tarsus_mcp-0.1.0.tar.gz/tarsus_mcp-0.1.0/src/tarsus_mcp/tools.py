from typing import Any, Dict, List, Callable, Optional
from tarsus import TarsusClient
from tarsus_client_generated.api.products import list_products_root_api_v1_products_get
from tarsus_client_generated.api.memory import search_knowledge_api_v1_memory_knowledge_search_get
from tarsus_client_generated.api.cart import get_cart_api_v1_cart_get

class TarsusTools:
    """
    Export Tarsus API tools in MCP/OpenAI Function format.
    """
    
    def __init__(self, client: TarsusClient):
        self.client = client
        self.authenticated_client = client.client

    def get_list_products_tool(self) -> Dict[str, Any]:
        """Return MCP-compatible tool definition for list_products."""
        return {
            "name": "list_products",
            "description": "List products from the store with pagination.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Number of products to return (default 10)", "default": 10},
                    "skip": {"type": "integer", "description": "Number of products to skip (default 0)", "default": 0}
                }
            },
            "callable": self._list_products_impl
        }

    def _list_products_impl(self, limit: int = 10, skip: int = 0) -> Any:
        # Using sync version for broader compatibility in simple scripts, 
        # or we could expose async if needed. Sticking to sync for universality in tools.
        return list_products_root_api_v1_products_get.sync(
            client=self.authenticated_client,
            limit=limit,
            skip=skip
        )

    def get_search_knowledge_tool(self) -> Dict[str, Any]:
        """Return MCP-compatible tool definition for search_knowledge."""
        return {
            "name": "search_knowledge",
            "description": "Search documentation and memory capabilities.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Max results", "default": 5}
                },
                "required": ["query"]
            },
            "callable": self._search_knowledge_impl
        }

    def _search_knowledge_impl(self, query: str, limit: int = 5) -> Any:
        return search_knowledge_api_v1_memory_knowledge_search_get.sync(
            client=self.authenticated_client,
            query=query,
            limit=limit
        )

    def get_cart_tool(self) -> Dict[str, Any]:
        """Return tool definition for get_cart."""
        return {
            "name": "get_cart",
            "description": "Get the current user's shopping cart.",
            "inputSchema": {
                "type": "object",
                "properties": {}
            },
            "callable": self._get_cart_impl
        }

    def _get_cart_impl(self) -> Any:
        return get_cart_api_v1_cart_get.sync(
            client=self.authenticated_client
        )

    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Return list of all tool definitions."""
        return [
            self.get_list_products_tool(),
            self.get_search_knowledge_tool(),
            self.get_cart_tool()
        ]
