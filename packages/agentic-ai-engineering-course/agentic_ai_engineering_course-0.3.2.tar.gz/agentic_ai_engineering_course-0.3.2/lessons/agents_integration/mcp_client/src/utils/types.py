"""Type definitions for client utilities."""

from enum import Enum
from typing import Optional


class InputType(Enum):
    """Types of user input that can be processed."""

    COMMAND_INFO_TOOLS = "command_info_tools"  # Show available tools
    COMMAND_INFO_RESOURCES = "command_info_resources"  # Show available resources
    COMMAND_INFO_PROMPTS = "command_info_prompts"  # Show available prompts
    COMMAND_UNKNOWN = "command_unknown"  # Unknown commands starting with "/"
    TERMINATE = "terminate"  # Commands that should terminate the app


class ProcessedInput:
    """Result of processing user input."""

    def __init__(
        self,
        input_type: InputType,
        should_continue: bool = True,
        user_message: Optional[str] = None,
    ):
        self.input_type = input_type
        self.should_continue = should_continue
        self.user_message = user_message
