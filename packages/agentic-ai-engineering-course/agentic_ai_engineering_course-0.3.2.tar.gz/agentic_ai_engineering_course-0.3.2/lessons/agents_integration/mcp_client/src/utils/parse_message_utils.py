"""Message parsing utilities."""

from .types import InputType, ProcessedInput


def parse_user_input(user_input: str) -> ProcessedInput:
    """Parse user input and return information about what type of input it is.

    This function only analyzes the input and returns metadata about how it should be handled.
    It does NOT execute any actions or modify any state.
    """

    user_input_lower = user_input.strip().lower()

    if user_input_lower == "/quit":
        # This is a termination command
        return ProcessedInput(input_type=InputType.TERMINATE, should_continue=False, user_message=user_input)

    # Check if this is a command starting with "/"
    if user_input_lower.startswith("/"):
        # This is a specific informational command
        if user_input_lower == "/tools":
            input_type = InputType.COMMAND_INFO_TOOLS
        elif user_input_lower == "/resources":
            input_type = InputType.COMMAND_INFO_RESOURCES
        elif user_input_lower == "/prompts":
            input_type = InputType.COMMAND_INFO_PROMPTS
        else:
            # Unknown command starting with "/", treat as invalid command
            input_type = InputType.COMMAND_UNKNOWN
    else:
        # Not a command, treat as unknown
        input_type = InputType.COMMAND_UNKNOWN

    return ProcessedInput(input_type=input_type, should_continue=True, user_message=user_input)
