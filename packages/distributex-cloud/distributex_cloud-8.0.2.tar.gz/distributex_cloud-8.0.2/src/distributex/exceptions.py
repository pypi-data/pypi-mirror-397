"""DistributeX exceptions."""


class DistributeXError(Exception):
    """Base exception for DistributeX SDK."""
    pass


class AuthenticationError(DistributeXError):
    """Raised when authentication fails."""
    pass


class JobError(DistributeXError):
    """Raised when a job operation fails."""
    pass


class RateLimitError(DistributeXError):
    """Raised when rate limit is exceeded."""
    pass
