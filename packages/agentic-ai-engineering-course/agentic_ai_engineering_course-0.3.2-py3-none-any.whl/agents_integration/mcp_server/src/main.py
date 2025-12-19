"""
Composed MCP Server - Combines Nova and Brown servers into a single endpoint.

This server uses FastMCP's composition features to mount both the Nova research agent
and Brown writing workflow servers with prefixes, exposing all their capabilities
through a single MCP server.

Usage:
    python -m src.main
"""

import json
import logging
from pathlib import Path

from fastmcp import Client, FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_server_config() -> dict:
    """Load the MCP servers configuration from JSON file."""
    config_path = Path(__file__).parent.parent / "mcp_servers_to_compose.json"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path) as f:
        return json.load(f)


def create_composed_server() -> FastMCP:
    """
    Create a composed MCP server by mounting Nova and Brown servers.
    
    Returns:
        FastMCP: The composed server instance with both servers mounted
    """
    # Create the main composed server
    mcp = FastMCP(
        name="Nova+Brown Composed Server",
        version="0.1.0",
    )
    
    logger.info("Loading server configuration...")
    config = load_server_config()
    
    servers_config = config.get("mcpServers", {})
    
    if not servers_config:
        raise ValueError("No servers found in configuration")
    
    logger.info(f"Found {len(servers_config)} servers to compose: {list(servers_config.keys())}")
    
    # Create proxies and mount each server
    for server_name, server_config in servers_config.items():
        logger.info(f"Creating proxy for {server_name}...")
        
        # Wrap the server config in the mcpServers structure expected by Client
        client_config = {"mcpServers": {server_name: server_config}}
        
        # Create a client for this server
        client = Client(client_config)
        
        # Create a proxy from the client
        proxy = FastMCP.as_proxy(client)
        
        # Determine the prefix to use (extract first part before hyphen)
        # nova-research-agent -> nova
        # brown-writing-workflow -> brown
        prefix = server_name.split("-")[0]
        
        logger.info(f"Mounting {server_name} with prefix '{prefix}'...")
        mcp.mount(proxy, prefix=prefix)
    
    logger.info("Composed server created successfully!")
    return mcp


if __name__ == "__main__":
    logger.info("Starting composed MCP server...")
    
    try:
        composed_server = create_composed_server()
        logger.info("Running composed server...")
        composed_server.run()
    except Exception as e:
        logger.error(f"Failed to start composed server: {e}")
        raise

