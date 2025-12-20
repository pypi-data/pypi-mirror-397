"""Send Message Module.

This module provides the Cloudbase Agent native send_message endpoint implementation,
including request models, event handlers, and server adapters.

Available Functions:
    - create_adapter: Create a FastAPI endpoint adapter for send_message
"""

from .server import create_adapter

__all__ = [
    "create_adapter",
]
