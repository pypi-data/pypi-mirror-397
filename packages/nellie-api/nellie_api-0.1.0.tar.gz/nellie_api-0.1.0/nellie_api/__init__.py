"""Nellie API Python SDK.

A Python client library for the Nellie AI Book Generation API.

Basic usage:
    >>> from nellie_api import Nellie
    >>>
    >>> client = Nellie(api_key="nel_...")
    >>> book = client.books.create(prompt="A mystery book")
    >>> print(book.request_id)
"""

from .client import (
    APIError,
    AuthenticationError,
    Nellie,
    NellieError,
    RateLimitError,
    __version__,
)
from .types import (
    Book,
    BookStatus,
    BookStyle,
    BookType,
    Configuration,
    CreateBookParams,
    Model,
    ModelVersion,
    OutputFormat,
    Usage,
    UsageRequest,
)
from .webhooks import Webhook, WebhookSignatureError

__all__ = [
    # Main client
    "Nellie",
    # Webhook utilities
    "Webhook",
    # Data types
    "Book",
    "CreateBookParams",
    "Model",
    "Configuration",
    "Usage",
    "UsageRequest",
    # Type literals
    "BookStyle",
    "BookType",
    "BookStatus",
    "ModelVersion",
    "OutputFormat",
    # Exceptions
    "NellieError",
    "APIError",
    "AuthenticationError",
    "RateLimitError",
    "WebhookSignatureError",
    # Version
    "__version__",
]
