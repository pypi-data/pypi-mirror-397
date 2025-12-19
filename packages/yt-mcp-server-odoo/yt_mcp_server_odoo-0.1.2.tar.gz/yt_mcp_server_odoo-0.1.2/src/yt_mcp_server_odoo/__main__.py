"""Entry point for the MCP server."""

import argparse
import logging
import sys

from dotenv import load_dotenv

from .config import get_config
from .server import OdooMCPServer


def main() -> None:
    """Main entry point for the MCP server."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="YourTechy MCP Server for Odoo")
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default=None,
        help="Transport type (default: stdio)"
    )
    parser.add_argument(
        "--host",
        default=None,
        help="Host for HTTP transport (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port for HTTP transport (default: 8000)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )
    
    # Get configuration
    config = get_config()
    
    # Override config with command line args
    if args.transport:
        config.mcp_transport = args.transport
    if args.host:
        config.mcp_host = args.host
    if args.port:
        config.mcp_port = args.port
    
    # Create and run server
    server = OdooMCPServer(config)
    
    try:
        logging.info(f"Starting MCP Server (transport: {config.mcp_transport})")
        server.run()
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    except Exception as e:
        logging.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
