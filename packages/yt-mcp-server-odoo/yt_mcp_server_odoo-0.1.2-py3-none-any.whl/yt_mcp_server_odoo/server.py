"""MCP Server for Odoo - Main server implementation."""

import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP

from .config import OdooConfig, get_config
from .odoo_connection import OdooConnection

logger = logging.getLogger(__name__)


class OdooMCPServer:
    """Main MCP server class for Odoo integration."""
    
    def __init__(self, config: Optional[OdooConfig] = None):
        self.config = config or get_config()
        self.connection: Optional[OdooConnection] = None
        
        # Create FastMCP application
        self.app = FastMCP(
            name="yt-mcp-server-odoo",
            instructions="MCP server for accessing and managing Odoo ERP data through the Model Context Protocol",
        )
        
        logger.info("Initialized YourTechy MCP Server for Odoo")
    
    async def _ensure_connection(self) -> OdooConnection:
        """Ensure we have an active connection to Odoo."""
        if self.connection is None or not self.connection.is_authenticated:
            self.connection = OdooConnection(self.config)
            await self.connection.connect()
        return self.connection
    
    def _register_tools(self) -> None:
        """Register all MCP tools."""
        
        @self.app.tool()
        async def search_records(
            model: str,
            domain: str = "[]",
            fields: Optional[str] = None,
            limit: int = 10,
            offset: int = 0,
            order: Optional[str] = None,
        ) -> str:
            """Search for records in an Odoo model.
            
            Args:
                model: The Odoo model name (e.g., 'res.partner')
                domain: Odoo domain filter as JSON string (default: "[]")
                fields: Optional comma-separated list of fields to return
                limit: Maximum number of records to return (default: 10)
                offset: Number of records to skip (default: 0)
                order: Sort order (e.g., 'name asc')
            
            Returns:
                Formatted search results
            """
            import json as json_module
            
            conn = await self._ensure_connection()
            
            # Parse domain from string
            parsed_domain = json_module.loads(domain) if domain else []
            
            # Parse fields
            parsed_fields = None
            if fields:
                parsed_fields = [f.strip() for f in fields.split(",")]
            
            result = await conn.search_records(
                model=model,
                domain=parsed_domain,
                fields=parsed_fields,
                limit=limit,
                offset=offset,
                order=order,
            )
            
            # Format output for LLM
            records = result.get("records", [])
            total = result.get("total", 0)
            
            lines = [
                f"Found {len(records)} of {total} records in {model}",
                "=" * 50,
            ]
            
            for record in records:
                lines.append(f"\n[ID: {record.get('id')}]")
                for key, value in record.items():
                    if key != "id":
                        lines.append(f"  {key}: {value}")
            
            return "\n".join(lines)
        
        @self.app.tool()
        async def get_record(
            model: str,
            record_id: int,
            fields: Optional[str] = None,
        ) -> str:
            """Get a specific record by ID.
            
            Args:
                model: The Odoo model name (e.g., 'res.partner')
                record_id: The record ID to retrieve
                fields: Optional comma-separated list of fields
            
            Returns:
                Formatted record data
            """
            conn = await self._ensure_connection()
            
            parsed_fields = None
            if fields:
                parsed_fields = [f.strip() for f in fields.split(",")]
            
            record = await conn.get_record(
                model=model,
                record_id=record_id,
                fields=parsed_fields,
            )
            
            # Format output
            lines = [
                f"Record: {model}/{record_id}",
                "=" * 50,
            ]
            
            for key, value in record.items():
                lines.append(f"{key}: {value}")
            
            return "\n".join(lines)
        
        @self.app.tool()
        async def create_record(
            model: str,
            values: str,
        ) -> str:
            """Create a new record in Odoo.
            
            Args:
                model: The Odoo model name (e.g., 'res.partner')
                values: JSON string of field values
            
            Returns:
                Confirmation with new record ID
            """
            import json as json_module
            
            conn = await self._ensure_connection()
            
            parsed_values = json_module.loads(values)
            result = await conn.create_record(model=model, values=parsed_values)
            
            record_id = result.get("id")
            return f"Created record: {model}/{record_id}"
        
        @self.app.tool()
        async def update_record(
            model: str,
            record_id: int,
            values: str,
        ) -> str:
            """Update an existing record.
            
            Args:
                model: The Odoo model name (e.g., 'res.partner')
                record_id: The record ID to update
                values: JSON string of field values to update
            
            Returns:
                Confirmation of update
            """
            import json as json_module
            
            conn = await self._ensure_connection()
            
            parsed_values = json_module.loads(values)
            await conn.update_record(
                model=model,
                record_id=record_id,
                values=parsed_values,
            )
            
            return f"Updated record: {model}/{record_id}"
        
        @self.app.tool()
        async def delete_record(
            model: str,
            record_id: int,
        ) -> str:
            """Delete a record from Odoo.
            
            Args:
                model: The Odoo model name (e.g., 'res.partner')
                record_id: The record ID to delete
            
            Returns:
                Confirmation of deletion
            """
            conn = await self._ensure_connection()
            
            await conn.delete_record(model=model, record_id=record_id)
            
            return f"Deleted record: {model}/{record_id}"
        
        @self.app.tool()
        async def list_models() -> str:
            """List all models enabled for MCP access.
            
            Returns:
                List of enabled models with their permissions
            """
            conn = await self._ensure_connection()
            
            result = await conn.list_models()
            models = result.get("models", {})
            
            lines = [
                f"Enabled Models ({len(models)} total)",
                "=" * 50,
            ]
            
            for model_name, permissions in models.items():
                perms = []
                if permissions.get("read"):
                    perms.append("R")
                if permissions.get("write"):
                    perms.append("W")
                if permissions.get("create"):
                    perms.append("C")
                if permissions.get("delete"):
                    perms.append("D")
                
                lines.append(f"{model_name} [{'/'.join(perms)}]")
            
            return "\n".join(lines)
        
        # ==================== NEW TOOLS ====================
        
        @self.app.tool()
        async def count_records(
            model: str,
            domain: str = "[]",
        ) -> str:
            """Count records matching a domain filter.
            
            Args:
                model: The Odoo model name (e.g., 'res.partner')
                domain: Odoo domain filter as JSON string (default: "[]")
            
            Returns:
                Count of matching records
            """
            import json as json_module
            
            conn = await self._ensure_connection()
            parsed_domain = json_module.loads(domain) if domain else []
            
            result = await conn.count_records(model=model, domain=parsed_domain)
            count = result.get("count", 0)
            
            return f"Count: {count} records in {model} matching {domain}"
        
        @self.app.tool()
        async def browse_records(
            model: str,
            ids: str,
            fields: Optional[str] = None,
        ) -> str:
            """Browse multiple records by their IDs.
            
            Args:
                model: The Odoo model name (e.g., 'res.partner')
                ids: Comma-separated list of record IDs (e.g., '1,2,3')
                fields: Optional comma-separated list of fields
            
            Returns:
                Formatted records data
            """
            conn = await self._ensure_connection()
            
            # Parse IDs
            parsed_ids = [int(id.strip()) for id in ids.split(",")]
            
            # Parse fields
            parsed_fields = None
            if fields:
                parsed_fields = [f.strip() for f in fields.split(",")]
            
            result = await conn.browse_records(
                model=model,
                ids=parsed_ids,
                fields=parsed_fields,
            )
            
            records = result.get("records", [])
            
            lines = [
                f"Retrieved {len(records)} records from {model}",
                "=" * 50,
            ]
            
            for record in records:
                lines.append(f"\n[ID: {record.get('id')}]")
                for key, value in record.items():
                    if key != "id":
                        lines.append(f"  {key}: {value}")
            
            return "\n".join(lines)
        
        @self.app.tool()
        async def create_bulk(
            model: str,
            records: str,
        ) -> str:
            """Create multiple records in a single request.
            
            Args:
                model: The Odoo model name (e.g., 'res.partner')
                records: JSON array of record dictionaries to create
            
            Returns:
                Created record IDs
            """
            import json as json_module
            
            conn = await self._ensure_connection()
            parsed_records = json_module.loads(records)
            
            result = await conn.create_bulk(model=model, records=parsed_records)
            
            created_ids = result.get("ids", [])
            errors = result.get("errors", [])
            
            lines = [f"Created {len(created_ids)} records in {model}"]
            lines.append(f"IDs: {created_ids}")
            
            if errors:
                lines.append(f"Errors: {errors}")
            
            return "\n".join(lines)
        
        @self.app.tool()
        async def update_bulk(
            model: str,
            updates: str,
        ) -> str:
            """Update multiple records with different values.
            
            Args:
                model: The Odoo model name (e.g., 'res.partner')
                updates: JSON array of {"id": record_id, "values": {...}}
            
            Returns:
                Updated record IDs
            """
            import json as json_module
            
            conn = await self._ensure_connection()
            parsed_updates = json_module.loads(updates)
            
            result = await conn.update_bulk(model=model, updates=parsed_updates)
            
            updated_ids = result.get("updated_ids", [])
            errors = result.get("errors", [])
            
            lines = [f"Updated {len(updated_ids)} records in {model}"]
            lines.append(f"IDs: {updated_ids}")
            
            if errors:
                lines.append(f"Errors: {errors}")
            
            return "\n".join(lines)
        
        @self.app.tool()
        async def list_prompts(
            category: Optional[str] = None,
            model: Optional[str] = None,
        ) -> str:
            """List available prompt templates for AI assistance.
            
            Args:
                category: Filter by category (search, create, update, report, analysis)
                model: Filter by model name (e.g., 'res.partner')
            
            Returns:
                List of prompt templates with examples
            """
            conn = await self._ensure_connection()
            
            result = await conn.list_prompt_templates(
                category=category,
                model=model,
            )
            
            templates = result.get("templates", [])
            
            lines = [
                f"Prompt Templates ({len(templates)} found)",
                "=" * 50,
            ]
            
            for t in templates:
                lines.append(f"\n[{t['category'].upper()}] {t['name']}")
                if t.get('description'):
                    lines.append(f"  Description: {t['description']}")
                if t.get('model'):
                    lines.append(f"  Model: {t['model']}")
                if t.get('example_input'):
                    lines.append(f"  Example: {t['example_input']}")
                lines.append(f"  Prompt: {t['prompt'][:100]}...")
            
            return "\n".join(lines)
    
    def run(self) -> None:
        """Run the MCP server."""
        self._register_tools()
        
        if self.config.mcp_transport == "streamable-http":
            self.app.run(
                transport="streamable-http",
                host=self.config.mcp_host,
                port=self.config.mcp_port,
            )
        else:
            self.app.run(transport="stdio")

