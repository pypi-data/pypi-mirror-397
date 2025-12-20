"""
Exception classes for Truslyo SDK
"""

class TruslyoError(Exception):
    """Base exception for Truslyo SDK"""
    pass


class FraudDetectedError(TruslyoError):
    """Raised when fraud is detected"""
    def __init__(self, message, result=None):
        super().__init__(message)
        self.result = result


class InvalidTokenError(TruslyoError):
    """Raised when token is invalid or expired"""
    pass


class APIError(TruslyoError):
    """Raised when API request fails"""
    pass


class RateLimitError(TruslyoError):
    """Raised when rate limit is exceeded"""
    pass