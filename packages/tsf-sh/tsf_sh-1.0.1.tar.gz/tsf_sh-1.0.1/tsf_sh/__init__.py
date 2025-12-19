"""
tsf-sh - Асинхронная Python библиотека для работы с tsf.sh API
"""

from .client import Client
from .exceptions import (
    Error,
    APIError,
    ValidationError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ConflictError,
    InternalServerError
)
from .models import Link, LinkStats, HealthStatus

__version__ = "1.0.0"
__all__ = [
    "Client",
    "Error",
    "APIError",
    "ValidationError",
    "UnauthorizedError",
    "ForbiddenError",
    "NotFoundError",
    "RateLimitError",
    "ConflictError",
    "InternalServerError",
    "Link",
    "LinkStats",
    "HealthStatus",
]

