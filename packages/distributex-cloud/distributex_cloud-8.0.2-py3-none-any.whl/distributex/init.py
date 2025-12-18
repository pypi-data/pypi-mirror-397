"""
DistributeX Python SDK

Official Python client for submitting and managing distributed computing jobs.
"""

from .client import DistributeX
from .exceptions import (
    DistributeXError,
    AuthenticationError,
    JobError,
    RateLimitError,
)

__version__ = "8.0.2"
__all__ = [
    "DistributeX",
    "DistributeXError",
    "AuthenticationError",
    "JobError",
    "RateLimitError",
]
