"""
Multi-Server MCP Client - Interactive MCP client connecting to multiple servers.

This client connects to both Nova (research agent) and Brown (writing workflow) 
MCP servers using a single FastMCP Client instance with multi-server configuration.

Usage:
    uv run python -m src.client
    uv run python -m src.client --config ../mcp_composed_server_config.json
"""

import argparse
import asyncio
import json
import logging
from pathlib import Path

from fastmcp import Client

from .settings import settings
from .utils.command_utils import handle_command
from .utils.logging_utils import configure_logging
from .utils.parse_message_utils import parse_user_input
from .utils.print_utils import Color, print_colored, print_header
from .utils.types import InputType

# Configure logging
configure_logging()


def print_welcome_message(server_name: str, tools: list, resources: list, prompts: list):
    """Print a welcome message for a server showing its capabilities count."""
    print_header(server_name.replace("-", " ").title())
    print(f"  - {len(tools)} tools available")
    print(f"  - {len(resources)} resources available")
    print(f"  - {len(prompts)} prompts available")
    print()


async def main():
    """Main function for the multi-server MCP client."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Multi-Server MCP Client")
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        default=None,
        help="Path to MCP servers config file (default: mcp_servers_config.json)",
    )
    args = parser.parse_args()
    
    # Determine which config file to use
    if args.config:
        config_path = Path(args.config)
        if not config_path.is_absolute():
            # Make it relative to the current working directory
            config_path = Path.cwd() / config_path
    else:
        config_path = settings.mcp_config_path
    
    try:
        # Load configuration from JSON file
        logging.info(f"Loading MCP server configuration from: {config_path}")
        with open(config_path) as f:
            config = json.load(f)

        server_names = list(config["mcpServers"].keys())
        logging.info(f"Found {len(server_names)} MCP servers in configuration: {', '.join(server_names)}")

        # Create a single client with multi-server configuration
        logging.info("Connecting to MCP servers...")
        client = Client(config)

        # Connect and fetch capabilities
        async with client:
            logging.info("Fetching capabilities from all servers...")
            tools = await client.list_tools()
            resources = await client.list_resources()
            prompts = await client.list_prompts()

            logging.info(
                f"Total capabilities: {len(tools)} tools, {len(resources)} resources, {len(prompts)} prompts"
            )

            # Print welcome message for each server
            # Extract server prefixes directly from tool names (works for both composed and direct configs)
            print()
            server_prefixes = set()
            for tool in tools:
                if "_" in tool.name:
                    prefix = tool.name.split("_")[0]
                    server_prefixes.add(prefix)
            
            for prefix in sorted(server_prefixes):
                prefix_tools = [t for t in tools if t.name.startswith(f"{prefix}_")]
                prefix_resources = [r for r in resources if prefix in str(r.uri)]
                prefix_prompts = [p for p in prompts if p.name.startswith(f"{prefix}_")]
                print_welcome_message(prefix, prefix_tools, prefix_resources, prefix_prompts)

            # Print available commands
            print("Available Commands: /tools, /resources, /prompts, /quit")
            print()

            # Main command loop
            while True:
                try:
                    # Get user input
                    user_input = input("> ").strip()
                    if not user_input:
                        continue

                    # Parse the user input
                    parsed_input = parse_user_input(user_input)

                    # Handle termination
                    if parsed_input.input_type == InputType.TERMINATE:
                        logging.info("👋 Terminating application...")
                        break

                    # Handle unknown commands
                    if parsed_input.input_type == InputType.COMMAND_UNKNOWN:
                        print_colored(
                            f"❌ Unknown command: '{parsed_input.user_message}'", Color.BRIGHT_RED
                        )
                        print("Available commands: /tools, /resources, /prompts, /quit")
                        print()
                        continue

                    # Handle informational commands
                    handle_command(parsed_input, tools, resources, prompts, server_names)

                except KeyboardInterrupt:
                    print()
                    logging.info("👋 Interrupted by user. Goodbye!")
                    break
                except Exception as e:
                    print()
                    logging.error(f"Error: {e}")
                    logging.info("Continuing...\n")

    except FileNotFoundError:
        logging.error(f"Configuration file not found: {settings.mcp_config_path}")
        logging.error("Please ensure mcp_servers_config.json exists in the mcp_client directory")
        return
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in configuration file: {e}")
        return
    except Exception as e:
        logging.error(f"Failed to initialize MCP client: {e}")
        return


if __name__ == "__main__":
    asyncio.run(main())
