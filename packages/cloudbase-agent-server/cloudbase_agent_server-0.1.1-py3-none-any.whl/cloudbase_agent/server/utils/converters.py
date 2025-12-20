#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Message and Tool Format Converters.

This module provides utility functions for converting between different
message and tool formats used in the Cloudbase Agent server.
"""

import json
import uuid
from typing import List

from ag_ui.core.types import (
    AssistantMessage,
    Message,
    RunAgentInput,
    SystemMessage,
    Tool,
    ToolMessage,
    UserMessage,
)
from pydantic import TypeAdapter

from ..send_message.models import ClientMessage
from ..send_message.models import Tool as AgKitTool

# Type annotation for client_message_adapter
client_message_adapter: TypeAdapter[ClientMessage] = TypeAdapter(ClientMessage)


def tools_to_agui_tools(tools: List[dict]) -> List[Tool]:
    """Convert client tools to AG-UI tool format.

    :param tools: List of raw tool dicts or None
    :type tools: List[dict] or None
    :return: List of converted Tool objects
    :rtype: List[Tool]
    :raises ValueError: If tool data is invalid
    """
    if not tools:
        return []
    agkit_tool_adapter = TypeAdapter(AgKitTool)
    return [tool_to_agui_tool(agkit_tool_adapter.validate_python(item)) for item in tools]


def messages_to_agui_messages(messages: List[dict]) -> List[Message]:
    """Convert client messages to AG-UI message format.

    :param messages: List of raw message dicts or None
    :type messages: List[dict] or None
    :return: List of converted Message objects
    :rtype: List[Message]
    :raises ValueError: If message data is invalid
    """
    if not messages:
        return []
    local_client_message_adapter: TypeAdapter[ClientMessage] = TypeAdapter(ClientMessage)
    return [message_to_agui_message(local_client_message_adapter.validate_python(item)) for item in messages]


def message_to_agui_message(message: ClientMessage) -> Message:
    """Convert single client message to AG-UI format.

    :param message: Input message in client format
    :type message: ClientMessage
    :return: Converted message in AG-UI format
    :rtype: Message
    :raises ValueError: If message role is invalid or missing required fields
    """
    message_id = str(uuid.uuid4())
    role = message.role
    content = message.content

    # Ensure content is not None
    safe_content = content or ""

    if role == "system":
        return SystemMessage(
            id=message_id,
            role=role,
            content=safe_content,
        )

    elif role == "user":
        return UserMessage(
            id=message_id,
            role=role,
            content=safe_content,
        )

    elif role == "tool":
        if not hasattr(message, "tool_call_id"):
            raise ValueError("Tool message must have tool_call_id")
        return ToolMessage(
            id=message_id,
            role=role,
            tool_call_id=message.tool_call_id,
            content=safe_content,
        )

    elif role == "assistant":
        return AssistantMessage(
            id=message_id,
            role=role,
            content=content,
            tool_calls=getattr(message, "tool_calls", None),
        )

    raise ValueError(f"Invalid message role: {role}")


def tool_to_agui_tool(tool: AgKitTool) -> Tool:
    """Convert single tool from Cloudbase Agent to AG-UI format.

    :param tool: Input tool in Cloudbase Agent format
    :type tool: AgKitTool
    :return: Converted tool in AG-UI format
    :rtype: Tool
    """
    return Tool(
        name=tool.name,
        description=tool.description,
        parameters=tool.parameters,
    )


def create_run_agent_input(input_data: dict) -> RunAgentInput:
    """Construct RunAgentInput from client request data.

    :param input_data: Raw input data from client
    :type input_data: dict
    :return: Structured RunAgentInput object
    :rtype: RunAgentInput
    :raises KeyError: If required fields are missing
    """
    return RunAgentInput(
        thread_id=input_data["conversationId"],
        run_id=str(uuid.uuid4()),
        state={},
        messages=messages_to_agui_messages(input_data.get("messages", [])),
        tools=tools_to_agui_tools(input_data.get("tools", [])),
        context=[],
        forwarded_props=create_forwarded_props(input_data),
    )


def create_forwarded_props(input_data: dict) -> dict:
    """Extract forwarded properties from input data.

    Processes resume commands and other forwarded properties from client requests.

    :param input_data: Raw input data from client
    :type input_data: dict
    :return: Dictionary of forwarded properties
    :rtype: dict
    """
    forwarded_props = {}
    resume_data = input_data.get("resume")
    if resume_data is not None:
        forwarded_props["command"] = {"resume": resume_data["payload"]}
    return forwarded_props


def is_valid_json(json_str: str) -> bool:
    """Check if string is valid JSON.

    :param json_str: String to validate
    :type json_str: str
    :return: True if valid JSON, False otherwise
    :rtype: bool
    """
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError:
        return False
