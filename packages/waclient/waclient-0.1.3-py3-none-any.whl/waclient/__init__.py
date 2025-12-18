"""WhatsApp Business Cloud API - Simplified Python SDK"""

__version__ = "0.1.0"
__author__ = "Your Name"

from .client import WhatsAppClient
from .exceptions import (
    WhatsAppError,
    AuthenticationError,
    MessageError,
    MediaError,
    WebhookError
)

__all__ = [
    "WhatsAppClient",
    "WhatsAppError",
    "AuthenticationError",
    "MessageError",
    "MediaError",
    "WebhookError"
]
