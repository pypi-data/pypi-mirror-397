"""
EnkaliPrime Python SDK

A Python client library for integrating with the EnkaliPrime Chat API.
Provides RAG-enabled AI chat functionality with session management and streaming support.
"""

from .client import EnkaliPrimeClient
from .models import (
    ChatMessage,
    ChatSession,
    ResolvedConnection,
    ChatApiConfig,
    ChatRequest,
    MessageStatus,
    MessageType,
)
from .exceptions import (
    EnkaliPrimeError,
    ConnectionError,
    AuthenticationError,
    APIError,
    StreamingError,
)

__version__ = "1.0.0"
__sdk_name__ = "enkaliprime-python-sdk"

__all__ = [
    # Main client
    "EnkaliPrimeClient",
    # Models
    "ChatMessage",
    "ChatSession",
    "ResolvedConnection",
    "ChatApiConfig",
    "ChatRequest",
    "MessageStatus",
    "MessageType",
    # Exceptions
    "EnkaliPrimeError",
    "ConnectionError",
    "AuthenticationError",
    "APIError",
    "StreamingError",
    # Version info
    "__version__",
    "__sdk_name__",
]

