#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OpenAI Format Converter.

This module provides conversion utilities between OpenAI API format
and Cloudbase Agent native format.
"""

from uuid import uuid4

from ..send_message.models import (
    AssistantMessage,
    SendMessageInput,
    SystemMessage,
    ToolMessage,
    UserMessage,
)
from .models import OpenAIChatCompletionRequest


def convert_openai_to_agkit(openai_request: OpenAIChatCompletionRequest) -> SendMessageInput:
    """Convert OpenAI chat completion request to Cloudbase Agent format.

    This function transforms OpenAI-compatible request format into Cloudbase Agent's
    native SendMessageInput format, enabling OpenAI API compatibility.

    :param openai_request: OpenAI-formatted chat completion request
    :type openai_request: OpenAIChatCompletionRequest
    :return: Cloudbase Agent formatted send message input
    :rtype: SendMessageInput

    Example:
        Converting an OpenAI request::

            openai_req = OpenAIChatCompletionRequest(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are helpful."},
                    {"role": "user", "content": "Hello!"}
                ]
            )
            agkit_req = convert_openai_to_agkit(openai_req)
    """
    # Convert messages
    agkit_messages = []
    for msg in openai_request.messages:
        if msg.role == "system":
            agkit_messages.append(SystemMessage(content=msg.content or ""))
        elif msg.role == "user":
            agkit_messages.append(UserMessage(content=msg.content or ""))
        elif msg.role == "assistant":
            agkit_messages.append(
                AssistantMessage(
                    id=str(uuid4()),
                    content=msg.content,
                    tool_calls=msg.tool_calls,
                )
            )
        elif msg.role == "tool":
            agkit_messages.append(
                ToolMessage(
                    content=msg.content or "",
                    tool_call_id=msg.tool_call_id or "",
                )
            )

    # Create Cloudbase Agent request
    return SendMessageInput(
        messages=agkit_messages,
        tools=openai_request.tools or [],
        conversationId=str(uuid4()),  # Generate new conversation ID
    )
