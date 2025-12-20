#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Send Message Data Models.

This module defines all the data models used for the send_message endpoint,
including request validation, message types, tool definitions, and event types.
"""

from typing import Any, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class ToolFunction(BaseModel):
    """Tool Function Definition Model.

    This model defines the structure of a function that can be called
    by an AI agent, including its name and serialized arguments.

    :param name: The name of the function to call
    :type name: str
    :param arguments: JSON-serialized function arguments as a string
    :type arguments: str

    Example:
        Creating a tool function call::

            func = ToolFunction(
                name="web_search",
                arguments='{"query": "Python tutorials", "limit": 5}'
            )
    """

    name: str
    arguments: str


class ToolCall(BaseModel):
    """Tool Function Call Model.

    This model represents an actual call to a tool function, including
    the unique call ID, type specification, and function details.

    :param id: Unique identifier for this tool call (used for tracking results)
    :type id: str
    :param type: Type of the call, always "function" for function calls
    :type type: Literal["function"]
    :param function: The function being called with its arguments
    :type function: ToolFunction

    Example:
        Creating a tool call::

            call = ToolCall(
                id="call_abc123",
                type="function",
                function=ToolFunction(
                    name="calculate",
                    arguments='{"expression": "2 + 2"}'
                )
            )
    """

    id: str
    type: Literal["function"] = "function"
    function: ToolFunction


class Tool(BaseModel):
    """Tool Definition Model.

    This model defines a tool that can be used by an AI agent,
    including its metadata and parameter schema for validation.

    :param name: The name of the tool (must be unique within a conversation)
    :type name: str
    :param description: Human-readable description of the tool's purpose
    :type description: str
    :param parameters: JSON schema defining the tool's input parameters
    :type parameters: Any

    Example:
        Defining a web search tool::

            tool = Tool(
                name="web_search",
                description="Search the web for information",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            )
    """

    name: str
    description: str
    parameters: Any


class BaseMessageModel(BaseModel):
    """Base Message Model.

    Base model with common configuration for all message types.
    Provides shared validation settings and field handling.
    """

    class Config:
        """Pydantic model configuration for message validation."""

        validate_by_name = True  # Allow both field names and aliases
        validate_assignment = True  # Validate on assignment after creation


class SystemMessage(BaseMessageModel):
    """System Message Model.

    System messages provide context and instructions to the AI agent
    about how it should behave in the conversation. These messages
    set the agent's personality, behavior rules, and operational context.

    :param role: Message role, always "system"
    :type role: Literal["system"]
    :param content: The system instruction content
    :type content: str

    Example:
        Creating a system message::

            sys_msg = SystemMessage(
                content="You are a helpful assistant that provides concise answers."
            )
    """

    role: Literal["system"] = "system"
    content: str


class UserMessage(BaseMessageModel):
    """User Message Model.

    User messages contain input from the human user to the AI agent.
    These represent the user's questions, requests, or conversational input.

    :param role: Message role, always "user"
    :type role: Literal["user"]
    :param content: The user's message content
    :type content: str

    Example:
        Creating a user message::

            user_msg = UserMessage(
                content="What's the weather like today?"
            )
    """

    role: Literal["user"] = "user"
    content: str


class ToolMessage(BaseMessageModel):
    """Tool Result Message Model.

    Tool messages contain the results of tool function executions
    that were requested by the AI agent. These messages provide
    the output data from external tool calls back to the agent.

    :param role: Message role, always "tool"
    :type role: Literal["tool"]
    :param content: The tool execution result as a string
    :type content: str
    :param tool_call_id: ID of the tool call this result corresponds to
    :type tool_call_id: str

    Example:
        Creating a tool result message::

            tool_msg = ToolMessage(
                content='{"results": ["Python Tutorial 1", "Python Guide 2"]}',
                tool_call_id="call_abc123"
            )

    Note:
        The tool_call_id must match the ID from the corresponding ToolCall
        that requested this execution.
    """

    role: Literal["tool"] = "tool"
    content: str
    tool_call_id: str = Field(..., alias="toolCallId")


class AssistantMessage(BaseMessageModel):
    """AI Assistant Message Model.

    Assistant messages contain responses from the AI agent, which may
    include text content and/or tool function calls. These represent
    the agent's output in the conversation.

    :param id: Unique identifier for this message
    :type id: str
    :param role: Message role, always "assistant"
    :type role: Literal["assistant"]
    :param content: The assistant's text response (optional if tool_calls present)
    :type content: Optional[str]
    :param tool_calls: List of tool calls made by the assistant (optional)
    :type tool_calls: Optional[List[ToolCall]]

    Example:
        Text response message::

            assistant_msg = AssistantMessage(
                id="msg_123",
                content="I can help you search for information."
            )

        Tool call message::

            assistant_msg = AssistantMessage(
                id="msg_124",
                content=None,
                tool_calls=[
                    ToolCall(
                        id="call_abc",
                        function=ToolFunction(name="search", arguments='{"q": "python"}')
                    )
                ]
            )

    Note:
        Either content or tool_calls (or both) should be present.
        Messages with only tool_calls typically have content=None.
    """

    id: str
    role: Literal["assistant"] = "assistant"
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = Field(None, alias="toolCalls")


ClientMessage = Union[SystemMessage, UserMessage, ToolMessage, AssistantMessage]
"""Union type for all possible client message types.

This type represents any message that can be sent by a client
in the conversation flow.
"""


class ResumeMessage(BaseModel):
    """Resume Message Model.

    This model represents a request to resume a conversation from a specific
    interruption point with the given payload data.

    :param interruptId: Unique identifier of the interruption to resume from
    :type interruptId: str
    :param payload: Serialized data required to resume the conversation
    :type payload: str
    """

    interruptId: str
    payload: str


class SendMessageInput(BaseMessageModel):
    """Send Message API Input Model.

    This model defines the structure of requests to the send message
    endpoint, including the conversation history, available tools,
    and conversation context.

    :param messages: List of conversation messages in chronological order
    :type messages: Optional[List[ClientMessage]]
    :param tools: Optional list of available tools for the agent to use
    :type tools: Optional[List[Tool]]
    :param resume: Optional resume message for interrupted conversations
    :type resume: Optional[ResumeMessage]
    :param conversationId: Unique identifier for the conversation thread
    :type conversationId: str

    Example:
        Creating a send message request::

            request = SendMessageInput(
                messages=[
                    SystemMessage(content="You are helpful."),
                    UserMessage(content="Hello!")
                ],
                tools=[
                    Tool(
                        name="calculator",
                        description="Perform calculations",
                        parameters={"type": "object", "properties": {...}}
                    )
                ],
                conversationId="conv_abc123"
            )

    Note:
        The conversationId is used for maintaining conversation state
        and should be consistent across messages in the same conversation.
    """

    messages: Optional[List[ClientMessage]] = []
    tools: Optional[List[Tool]] = []
    resume: Optional[ResumeMessage] = None
    conversationId: str


class BaseEvent(BaseModel):
    """Base Model for Event System.

    Provides common configuration for all event models in the system.
    Uses Pydantic's populate_by_name=True to allow field aliases.
    """

    model_config = ConfigDict(
        populate_by_name=True,
    )


class ErrorEvent(BaseEvent):
    """Error Event Model.

    Error events are sent when an error occurs during agent processing
    or request handling, providing error details to the client for
    appropriate error handling and user feedback.

    :param type: Event type, always "error"
    :type type: Literal["error"]
    :param error: Error message describing what went wrong
    :type error: str

    Example:
        Creating an error event::

            error_event = ErrorEvent(
                error="Agent execution failed: Invalid tool parameters"
            )
    """

    type: Literal["error"] = "error"
    error: str


class TextEvent(BaseEvent):
    """Text Streaming Event Model.

    Text events are used in streaming responses to send text content
    to the client as it becomes available from the AI agent. These
    events enable real-time text streaming for better user experience.

    :param type: Event type, always "text"
    :type type: Literal["text"]
    :param content: The text content chunk being streamed
    :type content: str

    Example:
        Creating a text event::

            text_event = TextEvent(
                content="Hello, I can help you with that question."
            )
    """

    type: Literal["text"] = "text"
    content: str


class ToolCallStartEvent(BaseEvent):
    """Tool Call Start Event Model.

    This event is sent when an AI agent begins executing a tool function,
    providing the tool call ID and function name to the client for
    tracking and UI updates.

    :param type: Event type, always "tool-call-start"
    :type type: Literal["tool-call-start"]
    :param tool_call_id: Unique identifier for this tool call
    :type tool_call_id: str
    :param tool_call_name: Name of the tool function being called
    :type tool_call_name: str

    Example:
        Creating a tool call start event::

            start_event = ToolCallStartEvent(
                tool_call_id="call_abc123",
                tool_call_name="web_search"
            )

    Note:
        This event is typically followed by ToolCallArgsEvent(s) and
        eventually a ToolCallEndEvent and ToolCallResultEvent.
    """

    type: Literal["tool-call-start"] = "tool-call-start"
    tool_call_id: str = Field(..., alias="toolCallId")
    tool_call_name: str = Field(..., alias="toolCallName")


class ToolCallArgsEvent(BaseEvent):
    """Model representing a tool call arguments streaming event.

    This event is sent during tool function execution to stream the
    function arguments as they are being constructed by the AI agent.

    :param type: Event type, always "tool-call-args"
    :type type: Literal["tool-call-args"]
    :param tool_call_id: Unique identifier for this tool call
    :type tool_call_id: str
    :param delta: Incremental argument data being streamed
    :type delta: str
    """

    type: Literal["tool-call-args"] = "tool-call-args"
    tool_call_id: str = Field(..., alias="toolCallId")
    delta: str


class ToolCallEndEvent(BaseEvent):
    """Model representing a tool call completion event.

    This event is sent when an AI agent finishes executing a tool function,
    indicating that the tool call has completed (successfully or with error).

    :param type: Event type, always "tool-end"
    :type type: Literal["tool-call-end"]
    :param tool_call_id: Unique identifier for the completed tool call
    :type tool_call_id: str
    """

    type: Literal["tool-call-end"] = "tool-call-end"
    tool_call_id: str = Field(..., alias="toolCallId")


class ToolCallResultEvent(BaseEvent):
    """Model representing a tool result streaming event.

    Tool result events are sent when a tool function execution
    completes and returns a result.

    :param type: Event type, always "tool-result"
    :type type: Literal["tool-result"]
    :param tool_call_id: ID of the tool call this result corresponds to
    :type tool_call_id: str
    :param result: The tool execution result
    :type result: str
    """

    type: Literal["tool-result"] = "tool-result"
    tool_call_id: str = Field(..., alias="toolCallId")
    result: str


class InterruptEvent(BaseEvent):
    """Interrupt Event Model.

    Interrupt events are sent when a streaming response is interrupted,
    typically for human-in-the-loop scenarios where user input is required
    before the agent can continue processing.

    :param type: Event type, always "interrupt"
    :type type: Literal["interrupt"]
    :param id: Unique identifier for the interrupt event
    :type id: str
    :param reason: Optional reason for the interruption
    :type reason: Optional[str]
    :param payload: Additional data related to the interruption (e.g., steps to approve)
    :type payload: Any

    Example:
        Creating an interrupt event for user approval::

            interrupt_event = InterruptEvent(
                id="interrupt_123",
                reason="User approval required for next steps",
                payload={
                    "steps": [
                        {"description": "Delete file", "status": "pending"},
                        {"description": "Send email", "status": "pending"}
                    ]
                }
            )

    Note:
        Interrupt events pause the agent execution until the client
        provides a response to resume processing.
    """

    type: Literal["interrupt"] = "interrupt"
    id: str
    reason: Optional[str] = None
    payload: Any


# Union event type for all streaming events
SendMessageEvent = Union[
    ErrorEvent, InterruptEvent, TextEvent, ToolCallArgsEvent, ToolCallEndEvent, ToolCallResultEvent, ToolCallStartEvent
]
"""Union type for all possible streaming event types.

This type represents any event that can be sent during
a streaming response.
"""
