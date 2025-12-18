"""Configuration management for Odoo MCP Server."""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class OdooConfig(BaseSettings):
    """Configuration for Odoo connection."""
    
    # Connection settings
    odoo_url: str = Field(
        default="http://localhost:8069",
        description="Odoo instance URL"
    )
    odoo_db: Optional[str] = Field(
        default=None,
        description="Database name (auto-detected if not set)"
    )
    
    # Authentication - API key preferred
    odoo_api_key: Optional[str] = Field(
        default=None,
        description="API key for authentication"
    )
    
    # Alternative authentication
    odoo_user: Optional[str] = Field(
        default=None,
        description="Username for authentication"
    )
    odoo_password: Optional[str] = Field(
        default=None,
        description="Password for authentication"
    )
    
    # Transport settings
    mcp_transport: str = Field(
        default="stdio",
        description="Transport type: stdio or streamable-http"
    )
    mcp_host: str = Field(
        default="localhost",
        description="Host for HTTP transport"
    )
    mcp_port: int = Field(
        default=8000,
        description="Port for HTTP transport"
    )
    
    # Operational settings
    default_limit: int = Field(
        default=10,
        description="Default number of records to return"
    )
    max_limit: int = Field(
        default=100,
        description="Maximum number of records per request"
    )
    max_smart_fields: int = Field(
        default=25,
        description="Maximum fields for smart selection"
    )
    
    # YOLO mode (development only)
    yolo_mode: Optional[str] = Field(
        default=None,
        alias="ODOO_YOLO",
        description="YOLO mode: off, read, true"
    )
    
    class Config:
        env_prefix = ""
        case_sensitive = False
        extra = "ignore"
    
    @property
    def is_yolo_enabled(self) -> bool:
        """Check if YOLO mode is enabled."""
        return self.yolo_mode in ("read", "true")
    
    @property
    def is_yolo_write(self) -> bool:
        """Check if YOLO mode allows writes."""
        return self.yolo_mode == "true"


_config: Optional[OdooConfig] = None


def get_config() -> OdooConfig:
    """Get or create the global configuration instance."""
    global _config
    if _config is None:
        _config = OdooConfig()
    return _config
