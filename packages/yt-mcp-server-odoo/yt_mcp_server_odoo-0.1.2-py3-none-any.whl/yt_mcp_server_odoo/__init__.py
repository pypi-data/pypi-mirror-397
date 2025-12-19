"""YourTechy MCP Server for Odoo.

This package enables AI assistants like Claude to interact with Odoo ERP
through the Model Context Protocol (MCP).
"""

__version__ = "0.1.0"

from .config import OdooConfig, get_config
from .server import OdooMCPServer

__all__ = ["OdooConfig", "get_config", "OdooMCPServer", "__version__"]
