#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HTTP Request Handler for Send Message.

This module provides HTTP protocol-level mapping and request handling
for the Cloudbase Agent send_message endpoint. It processes incoming requests,
converts between client and internal message formats, and manages agent
execution with real-time event streaming support.

Key Features:
    - Message format conversion between client API and AG-UI formats
    - Tool definition mapping and validation
    - Event streaming with proper type conversion
    - Error handling and recovery mechanisms
    - Support for various event types (text, tool calls, interrupts)
"""

import json
from typing import Any, AsyncGenerator

from ag_ui.core.events import EventType

from ..utils.converters import create_run_agent_input, is_valid_json
from .models import (
    InterruptEvent,
    SendMessageEvent,
    TextEvent,
    ToolCallArgsEvent,
    ToolCallEndEvent,
    ToolCallResultEvent,
    ToolCallStartEvent,
)


async def handler(input_data: dict, agent: Any) -> AsyncGenerator[SendMessageEvent, None]:
    """Handle HTTP requests and process agent execution with streaming.

    This function serves as the main request handler for the send_message endpoint.
    It converts client messages to the internal AG-UI format, executes the agent,
    and streams back the results as properly formatted events for client consumption.

    Processing Flow:
        1. Convert client messages to AG-UI message format
        2. Convert client tools to AG-UI tool format
        3. Create RunAgentInput with conversation context
        4. Execute agent and process streaming events
        5. Convert AG-UI events to client event format

    :param input_data: Dictionary containing request data with messages, tools, and conversation ID
    :type input_data: dict
    :param agent: The agent instance to execute (must have a 'run' method)
    :type agent: Any

    :yields: Formatted event objects for client consumption
    :ytype: SendMessageEvent

    :raises RuntimeError: When agent execution or message processing fails

    Example:
        Processing a chat request with tools::

            input_data = {
                'conversationId': 'conv_123',
                'messages': [
                    {'role': 'user', 'content': 'Search for Python tutorials'}
                ],
                'tools': [
                    {
                        'name': 'web_search',
                        'description': 'Search the web',
                        'parameters': {'type': 'object', 'properties': {...}}
                    }
                ]
            }

            async for event in handler(input_data, my_agent):
                if event.type == 'text':
                    print(f"AI Response: {event.content}")
                elif event.type == 'tool-call-start':
                    print(f"Tool Call: {event.tool_call_name}")
    """
    try:
        run_data = create_run_agent_input(input_data)

        async for event in agent.run(run_data):
            match event.type:
                case EventType.TEXT_MESSAGE_CONTENT:
                    data = {"content": event.raw_event["data"]["chunk"]["content"]}
                    yield TextEvent.model_validate(data)
                case EventType.TEXT_MESSAGE_CHUNK:
                    content = None
                    if event.raw_event:
                        content = event.raw_event.get("data", {}).get("chunk", {}).get("content")
                    if content is None:
                        content = event.delta
                    data = {"content": content}
                    yield TextEvent.model_validate(data)
                case EventType.TOOL_CALL_START:
                    data = {"tool_call_id": event.tool_call_id, "tool_call_name": event.tool_call_name}
                    yield ToolCallStartEvent.model_validate(data)
                    start_delta = None
                    if event.raw_event is not None:
                        start_delta = (
                            event.raw_event.get("data", {})
                            .get("chunk", {})
                            .get("tool_call_chunks", [{}])[0]
                            .get("args")
                        )
                    if start_delta is not None:
                        data = {"tool_call_id": event.tool_call_id, "delta": start_delta}
                        yield ToolCallArgsEvent.model_validate(data)
                case EventType.TOOL_CALL_ARGS:
                    data = {"tool_call_id": event.tool_call_id, "delta": event.delta}
                    yield ToolCallArgsEvent.model_validate(data)
                case EventType.TOOL_CALL_CHUNK:
                    data = {"tool_call_id": event.tool_call_id, "delta": event.delta}
                    yield ToolCallArgsEvent.model_validate(data)
                case EventType.TOOL_CALL_END:
                    data = {"tool_call_id": event.tool_call_id}
                    yield ToolCallEndEvent.model_validate(data)
                case EventType.TOOL_CALL_RESULT:
                    data = {"tool_call_id": event.tool_call_id, "result": event.content}
                    yield ToolCallResultEvent.model_validate(data)
                case EventType.CUSTOM:
                    if event.name == "on_interrupt":
                        if isinstance(event.value, str) and is_valid_json(event.value):
                            data = {
                                "id": event.raw_event,
                                "payload": json.loads(event.value),
                                "reason": "agent requested interrupt",
                            }
                            yield InterruptEvent.model_validate(data)
                    pass
                case _:
                    pass

    except Exception as e:
        raise RuntimeError(f"Failed to send: {str(e)}") from e
