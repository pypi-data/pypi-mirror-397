"""Odoo connection handler using REST API."""

import logging
from typing import Any, Dict, List, Optional

import httpx

from .config import OdooConfig

logger = logging.getLogger(__name__)


class OdooConnectionError(Exception):
    """Exception for Odoo connection errors."""
    pass


class OdooConnection:
    """Handles connection to Odoo via REST API."""
    
    def __init__(self, config: OdooConfig):
        self.config = config
        self.client: Optional[httpx.AsyncClient] = None
        self._authenticated = False
        self._user_info: Optional[Dict[str, Any]] = None
    
    @property
    def is_authenticated(self) -> bool:
        return self._authenticated
    
    async def connect(self) -> None:
        """Establish connection to Odoo."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        if self.config.odoo_api_key:
            headers["X-MCP-API-KEY"] = self.config.odoo_api_key
        
        if self.config.odoo_db:
            headers["X-Odoo-Database"] = self.config.odoo_db
        
        self.client = httpx.AsyncClient(
            base_url=self.config.odoo_url,
            headers=headers,
            timeout=30.0,
        )
        
        # Verify connection
        try:
            response = await self.client.get("/mcp/health")
            if response.status_code == 200:
                self._authenticated = True
                logger.info(f"Connected to Odoo at {self.config.odoo_url}")
                
                # Validate API key if provided
                if self.config.odoo_api_key:
                    await self._validate_api_key()
            else:
                raise OdooConnectionError(f"Health check failed: {response.status_code}")
        except httpx.RequestError as e:
            raise OdooConnectionError(f"Failed to connect to Odoo: {e}") from e
    
    async def _validate_api_key(self) -> None:
        """Validate the API key."""
        response = await self.client.post("/mcp/auth/validate", json={})
        if response.status_code == 200:
            data = response.json()
            if data.get("valid"):
                self._user_info = {
                    "id": data.get("user_id"),
                    "name": data.get("user_name"),
                    "login": data.get("user_login"),
                }
                logger.info(f"Authenticated as {self._user_info['name']}")
            else:
                raise OdooConnectionError("Invalid API key")
        else:
            raise OdooConnectionError(f"API key validation failed: {response.status_code}")
    
    async def disconnect(self) -> None:
        """Close the connection."""
        if self.client:
            await self.client.aclose()
            self.client = None
            self._authenticated = False
    
    async def search_records(
        self,
        model: str,
        domain: Optional[List] = None,
        fields: Optional[List[str]] = None,
        limit: int = 10,
        offset: int = 0,
        order: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Search records in a model."""
        if not self.client:
            raise OdooConnectionError("Not connected")
        
        data = {
            "domain": domain or [],
            "limit": limit,
            "offset": offset,
        }
        if fields:
            data["fields"] = fields
        if order:
            data["order"] = order
        
        response = await self.client.post(f"/mcp/models/{model}/search", json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            raise OdooConnectionError(error_data.get("error", "Search failed"))
    
    async def get_record(
        self,
        model: str,
        record_id: int,
        fields: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get a specific record by ID."""
        if not self.client:
            raise OdooConnectionError("Not connected")
        
        data = {"ids": [record_id]}
        if fields:
            data["fields"] = fields
        
        response = await self.client.post(f"/mcp/models/{model}/read", json=data)
        
        if response.status_code == 200:
            result = response.json()
            records = result.get("records", [])
            if records:
                return records[0]
            raise OdooConnectionError(f"Record {model}/{record_id} not found")
        else:
            error_data = response.json()
            raise OdooConnectionError(error_data.get("error", "Read failed"))
    
    async def create_record(
        self,
        model: str,
        values: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a new record."""
        if not self.client:
            raise OdooConnectionError("Not connected")
        
        response = await self.client.post(
            f"/mcp/models/{model}/create",
            json={"values": values}
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            error_data = response.json()
            raise OdooConnectionError(error_data.get("error", "Create failed"))
    
    async def update_record(
        self,
        model: str,
        record_id: int,
        values: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update an existing record."""
        if not self.client:
            raise OdooConnectionError("Not connected")
        
        response = await self.client.post(
            f"/mcp/models/{model}/write",
            json={"ids": [record_id], "values": values}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            raise OdooConnectionError(error_data.get("error", "Update failed"))
    
    async def delete_record(
        self,
        model: str,
        record_id: int,
    ) -> Dict[str, Any]:
        """Delete a record."""
        if not self.client:
            raise OdooConnectionError("Not connected")
        
        response = await self.client.post(
            f"/mcp/models/{model}/unlink",
            json={"ids": [record_id]}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            raise OdooConnectionError(error_data.get("error", "Delete failed"))
    
    async def list_models(self) -> Dict[str, Any]:
        """List all enabled models."""
        if not self.client:
            raise OdooConnectionError("Not connected")
        
        response = await self.client.get("/mcp/models")
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            raise OdooConnectionError(error_data.get("error", "List models failed"))
    
    async def get_model_fields(self, model: str) -> Dict[str, Any]:
        """Get field definitions for a model."""
        if not self.client:
            raise OdooConnectionError("Not connected")
        
        response = await self.client.get(f"/mcp/models/{model}/fields")
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            raise OdooConnectionError(error_data.get("error", "Get fields failed"))
    
    # ==================== NEW BULK OPERATIONS ====================
    
    async def count_records(
        self,
        model: str,
        domain: Optional[List] = None,
    ) -> Dict[str, Any]:
        """Count records matching a domain."""
        if not self.client:
            raise OdooConnectionError("Not connected")
        
        data = {"domain": domain or []}
        response = await self.client.post(f"/mcp/models/{model}/count", json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            raise OdooConnectionError(error_data.get("error", "Count failed"))
    
    async def browse_records(
        self,
        model: str,
        ids: List[int],
        fields: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Browse multiple records by IDs."""
        if not self.client:
            raise OdooConnectionError("Not connected")
        
        data = {"ids": ids}
        if fields:
            data["fields"] = fields
        
        response = await self.client.post(f"/mcp/models/{model}/browse", json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            raise OdooConnectionError(error_data.get("error", "Browse failed"))
    
    async def create_bulk(
        self,
        model: str,
        records: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Create multiple records in bulk."""
        if not self.client:
            raise OdooConnectionError("Not connected")
        
        response = await self.client.post(
            f"/mcp/models/{model}/create_bulk",
            json={"records": records}
        )
        
        if response.status_code in (200, 201):
            return response.json()
        else:
            error_data = response.json()
            raise OdooConnectionError(error_data.get("error", "Bulk create failed"))
    
    async def update_bulk(
        self,
        model: str,
        updates: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Update multiple records with different values.
        
        Args:
            model: Model name
            updates: List of {"id": record_id, "values": {...}}
        """
        if not self.client:
            raise OdooConnectionError("Not connected")
        
        response = await self.client.post(
            f"/mcp/models/{model}/write_bulk",
            json={"updates": updates}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            raise OdooConnectionError(error_data.get("error", "Bulk update failed"))
    
    # ==================== PROMPT TEMPLATES ====================
    
    async def list_prompt_templates(
        self,
        category: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List available prompt templates.
        
        Args:
            category: Filter by category (search, create, update, etc.)
            model: Filter by model name
        """
        if not self.client:
            raise OdooConnectionError("Not connected")
        
        params = {}
        if category:
            params["category"] = category
        if model:
            params["model"] = model
        
        response = await self.client.get("/mcp/prompts", params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            raise OdooConnectionError(error_data.get("error", "List templates failed"))
    
    async def get_prompt_template(self, template_id: int) -> Dict[str, Any]:
        """Get a specific prompt template by ID."""
        if not self.client:
            raise OdooConnectionError("Not connected")
        
        response = await self.client.get(f"/mcp/prompts/{template_id}")
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            raise OdooConnectionError(error_data.get("error", "Get template failed"))
