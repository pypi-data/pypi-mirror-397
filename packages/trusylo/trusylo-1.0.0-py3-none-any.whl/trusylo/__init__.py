"""
Truslyo Fraud Detection SDK for Python

Stop fraud with one line of code:

    from trusylo import trusylo_protect
    
    @app.post("/signup")
    @trusylo_protect(api_key="sk_live_abc123")
    async def signup(request):
        # Your code here
        return {"success": True}

Documentation: https://docs.trusylo.com
"""

__version__ = "1.0.0"

from .client import TruslyoClient
from .decorators import trusylo_protect
from .middleware import TruslyoMiddleware
from .exceptions import (
    TruslyoError,
    FraudDetectedError,
    InvalidTokenError,
    APIError,
    RateLimitError
)

__all__ = [
    "TruslyoClient",
    "trusylo_protect",
    "TruslyoMiddleware",
    "TruslyoError",
    "FraudDetectedError",
    "InvalidTokenError",
    "APIError",
    "RateLimitError"
]