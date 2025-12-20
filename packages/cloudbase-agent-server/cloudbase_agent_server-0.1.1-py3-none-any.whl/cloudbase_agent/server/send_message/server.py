#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Send Message Server Adapter.

This module provides the server adapter for the send_message endpoint,
handling request processing, streaming responses, and resource cleanup.
"""

import inspect
import json
from typing import AsyncGenerator

from fastapi.responses import StreamingResponse
from pydantic import ValidationError

from ..utils.sse import async_generator_from_string
from ..utils.types import AgentCreator
from .handler import handler
from .models import SendMessageInput


async def create_adapter(create_agent: AgentCreator, request: SendMessageInput) -> StreamingResponse:
    r"""Create a FastAPI adapter for send_message requests with streaming support.

    This function creates a streaming HTTP response adapter that processes
    send_message requests and returns Server-Sent Events (SSE) formatted responses.
    It handles the complete request lifecycle including validation, processing,
    event streaming, resource cleanup, and error recovery.

    Processing Flow:
        1. Create agent instance via create_agent function
        2. Convert request to internal format
        3. Create SSE stream generator
        4. Process agent events and format as SSE
        5. Send completion marker
        6. Call cleanup function if provided

    :param create_agent: Function that creates and returns agent with optional cleanup
    :type create_agent: AgentCreator
    :param request: The validated request input containing messages and tools
    :type request: SendMessageInput

    :return: Streaming response with SSE-formatted events and proper headers
    :rtype: StreamingResponse

    :raises ValidationError: When request validation fails
    :raises Exception: When agent processing fails or other errors occur

    Example:
        Using the adapter in a FastAPI route::

            from fastapi import FastAPI
            from cloudbase_agent.server.send_message import create_adapter
            from cloudbase_agent.schemas import SendMessageInput

            def create_agent():
                db = connect_database()
                agent = MyAgent(db)
                return {
                    "agent": agent,
                    "cleanup": lambda: db.close()
                }

            app = FastAPI()

            @app.post("/send-message")
            async def send_message_endpoint(request: SendMessageInput):
                return await create_adapter(create_agent, request)

    Note:
        The response uses Server-Sent Events format with proper headers
        for streaming. Each event is formatted as "data: {json}\\n\\n".
        The cleanup function is guaranteed to be called after the stream
        completes, even if errors occur.
    """
    try:
        # Create agent and get optional cleanup function
        result = create_agent()
        if inspect.iscoroutine(result):
            result = await result

        agent = result["agent"]
        cleanup = result.get("cleanup")

        input_data = request.model_dump()

        async def create_sse_stream() -> AsyncGenerator[str, None]:
            """Create Server-Sent Events stream with cleanup support.

            This internal generator function processes agent events and formats
            them as Server-Sent Events for streaming HTTP responses. It ensures
            the cleanup function is called after streaming completes.

            :yields: SSE-formatted event strings
            :ytype: str
            """
            try:
                async for event in handler(input_data, agent):
                    sse_chunk = f"data: {event.model_dump_json(by_alias=True, ensure_ascii=False)}\n\n"
                    yield sse_chunk

                yield "data: [DONE]\n\n"
            finally:
                # Ensure cleanup is called even if errors occur
                if cleanup:
                    if inspect.iscoroutinefunction(cleanup):
                        await cleanup()
                    else:
                        cleanup()

        return StreamingResponse(
            create_sse_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache, no-transform",
                "Connection": "keep-alive",
            },
        )

    except ValidationError as e:
        # Handle validation errors
        error_stream = async_generator_from_string(
            f"data: {json.dumps({'error': 'Validation failed', 'details': str(e)})}\n\n"
        )
        return StreamingResponse(error_stream, media_type="text/event-stream")

    except Exception as e:
        # Handle other errors
        error_stream = async_generator_from_string(
            f"data: {json.dumps({'error': 'Server error', 'details': str(e)})}\n\n"
        )
        return StreamingResponse(error_stream, media_type="text/event-stream")
