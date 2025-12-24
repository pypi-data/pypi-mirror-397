from .client import HealthSecureClient
from .types import (
    SignalPayload,
    SignalResponse,
    PolicyContext,
    ExecutionContextV2,
    ConfidenceBand,
)
from .exceptions import (
    HealthSecureError,
    AuthenticationError,
    RateLimitError,
    APIError
)
from .extract import (
    extract_from_json,
    extract_from_text,
    extract_v2_json,
    extract_v2_text,
)
from .helpers import build_v2_signal
from .llm_wrapper import safe_llm_call

__version__ = "0.2.0.post1"

__all__ = [
    # v1 exports
    "HealthSecureClient",
    "SignalPayload",
    "SignalResponse",
    "HealthSecureError",
    "AuthenticationError",
    "RateLimitError",
    "APIError",
    "extract_from_json",
    "extract_from_text",
    "safe_llm_call",
    # v2 exports
    "extract_v2_json",
    "extract_v2_text",
    "build_v2_signal",
    "PolicyContext",
    "ExecutionContextV2",
    "ConfidenceBand",
]

