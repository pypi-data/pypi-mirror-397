"""Command handling utilities."""

import logging
from typing import List

from .print_utils import Color, print_header, print_item
from .types import InputType, ProcessedInput

logger = logging.getLogger(__name__)


def handle_command(
    processed_input: ProcessedInput, tools: List, resources: List, prompts: List, server_names: List[str]
):
    """Handle informational commands by grouping capabilities by server prefix.

    Args:
        processed_input: The parsed user input
        tools: List of all tools from all servers (with server prefixes)
        resources: List of all resources from all servers
        prompts: List of all prompts from all servers (with server prefixes)
        server_names: List of server names from the configuration (unused, kept for compatibility)
    """
    # Extract server prefixes directly from tool names (works for both composed and direct configs)
    server_prefixes = set()
    for tool in tools:
        if "_" in tool.name:
            prefix = tool.name.split("_")[0]
            server_prefixes.add(prefix)
    
    if processed_input.input_type == InputType.COMMAND_INFO_TOOLS:
        for prefix in sorted(server_prefixes):
            prefix_tools = [t for t in tools if t.name.startswith(f"{prefix}_")]
            if prefix_tools:
                print_header(f"{prefix} - Tools ({len(prefix_tools)})")
                for i, tool in enumerate(prefix_tools, 1):
                    print_item(tool.name, tool.description, i, Color.BRIGHT_WHITE, Color.YELLOW)

    elif processed_input.input_type == InputType.COMMAND_INFO_RESOURCES:
        for prefix in sorted(server_prefixes):
            prefix_resources = [r for r in resources if prefix in str(r.uri)]
            if prefix_resources:
                print_header(f"{prefix} - Resources ({len(prefix_resources)})")
                for i, resource in enumerate(prefix_resources, 1):
                    print_item(str(resource.uri), resource.description, i, Color.BRIGHT_WHITE, Color.YELLOW)

    elif processed_input.input_type == InputType.COMMAND_INFO_PROMPTS:
        for prefix in sorted(server_prefixes):
            prefix_prompts = [p for p in prompts if p.name.startswith(f"{prefix}_")]
            if prefix_prompts:
                print_header(f"{prefix} - Prompts ({len(prefix_prompts)})")
                for i, prompt in enumerate(prefix_prompts, 1):
                    print_item(prompt.name, prompt.description, i, Color.BRIGHT_WHITE, Color.YELLOW)
