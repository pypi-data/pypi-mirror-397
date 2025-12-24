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
from .config import SDKConfig, SuppressionStore, get_default_config, get_default_suppression
from .sdk_helpers import (
    analyze_api_response,
    analyze_llm_output,
    analyze_log_entry,
    format_response_for_logging,
)

__version__ = "0.3.0"

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
    # v3 exports (0.3.0-beta)
    "SDKConfig",
    "SuppressionStore",
    "get_default_config",
    "get_default_suppression",
    "analyze_api_response",
    "analyze_llm_output",
    "analyze_log_entry",
    "format_response_for_logging",
]

