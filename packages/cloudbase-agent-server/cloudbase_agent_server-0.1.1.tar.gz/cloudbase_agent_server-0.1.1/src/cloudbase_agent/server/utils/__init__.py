"""Utility Functions Package.

This package provides common utility functions and types used across
the Cloudbase Agent server implementation.

Available Modules:
    - types: Type definitions for agent creators and results
    - sse: Server-Sent Events utilities
    - converters: Message and tool format conversion utilities
"""

from .converters import (
    create_run_agent_input,
    is_valid_json,
    message_to_agui_message,
    messages_to_agui_messages,
    tool_to_agui_tool,
    tools_to_agui_tools,
)
from .sse import async_generator_from_string
from .types import AgentCreator, AgentCreatorResult

__all__ = [
    "AgentCreator",
    "AgentCreatorResult",
    "create_run_agent_input",
    "is_valid_json",
    "message_to_agui_message",
    "messages_to_agui_messages",
    "tool_to_agui_tool",
    "tools_to_agui_tools",
    "async_generator_from_string",
]
