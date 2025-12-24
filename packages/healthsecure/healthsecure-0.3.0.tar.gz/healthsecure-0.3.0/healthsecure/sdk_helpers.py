"""
Helper functions for common SDK usage patterns.
"""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone

from .types import SignalPayload, SignalResponse, PolicyContext, ExecutionContextV2
from .extract import extract_v2_json, extract_v2_text
from .helpers import build_v2_signal
from .client import HealthSecureClient
from .config import SDKConfig, get_default_config, get_default_suppression
from .utils.confidence import confidence_to_band


def analyze_api_response(
    response_data: Any,
    client: HealthSecureClient,
    *,
    source: str = "api_response",
    region: str = "GLOBAL",
    environment: str = "production",
    config: Optional[SDKConfig] = None,
) -> Tuple[Optional[SignalResponse], bool]:
    """
    Analyze an API response for sensitive data exposure.
    
    Args:
        response_data: API response data (dict, list, or any JSON-serializable)
        client: HealthSecureClient instance
        source: Signal source (default: "api_response")
        region: Region code (default: "GLOBAL")
        environment: Environment (default: "production")
        config: Optional SDK configuration
    
    Returns:
        Tuple of (SignalResponse if sent, was_suppressed)
    """
    config = config or get_default_config()
    suppression = get_default_suppression()
    
    # Extract
    extract_result = extract_v2_json(response_data)
    
    # Check if blocked
    if config.should_block(extract_result["detected_data_classes"]):
        return None, False
    
    # Check confidence threshold
    if not config.should_send(extract_result.get("confidence_band")):
        return None, False
    
    # Build signal
    signal = build_v2_signal(
        extract_result,
        source=source,
        region=region,
        environment=environment,
        policy=PolicyContext(
            min_confidence=config.min_confidence_band,
            blocked_classes=config.blocked_data_classes if config.blocked_data_classes else None,
        ),
        context=ExecutionContextV2(
            channel="api",
            mode="monitor",
        ),
    )
    
    # Check suppression
    if config.enable_suppression and suppression.is_suppressed(signal.fingerprint):
        return None, True
    
    # Send signal
    try:
        response = client.analyze_signal(signal)
        suppression.record(signal.fingerprint)
        return response, False
    except Exception:
        # Don't fail the API call if signal sending fails
        return None, False


def analyze_llm_output(
    llm_text: str,
    client: HealthSecureClient,
    *,
    source: str = "llm_response",
    region: str = "GLOBAL",
    environment: str = "production",
    config: Optional[SDKConfig] = None,
) -> Tuple[Optional[SignalResponse], bool]:
    """
    Analyze LLM output text for sensitive data exposure.
    
    Args:
        llm_text: LLM response text
        client: HealthSecureClient instance
        source: Signal source (default: "llm_response")
        region: Region code (default: "GLOBAL")
        environment: Environment (default: "production")
        config: Optional SDK configuration
    
    Returns:
        Tuple of (SignalResponse if sent, was_suppressed)
    """
    config = config or get_default_config()
    suppression = get_default_suppression()
    
    # Extract
    extract_result = extract_v2_text(llm_text)
    
    # Check if blocked
    if config.should_block(extract_result["detected_data_classes"]):
        return None, False
    
    # Check confidence threshold
    if not config.should_send(extract_result.get("confidence_band")):
        return None, False
    
    # Build signal
    signal = build_v2_signal(
        extract_result,
        source=source,
        region=region,
        environment=environment,
        policy=PolicyContext(
            min_confidence=config.min_confidence_band,
            blocked_classes=config.blocked_data_classes if config.blocked_data_classes else None,
        ),
        context=ExecutionContextV2(
            channel="llm",
            mode="monitor",
        ),
    )
    
    # Check suppression
    if config.enable_suppression and suppression.is_suppressed(signal.fingerprint):
        return None, True
    
    # Send signal
    try:
        response = client.analyze_signal(signal)
        suppression.record(signal.fingerprint)
        return response, False
    except Exception:
        # Don't fail the LLM call if signal sending fails
        return None, False


def analyze_log_entry(
    log_data: Any,
    client: HealthSecureClient,
    *,
    source: str = "service_response",
    region: str = "GLOBAL",
    environment: str = "production",
    config: Optional[SDKConfig] = None,
) -> Tuple[Optional[SignalResponse], bool]:
    """
    Analyze a log entry for sensitive data exposure.
    
    Args:
        log_data: Log data (dict, string, or any JSON-serializable)
        client: HealthSecureClient instance
        source: Signal source (default: "service_response")
        region: Region code (default: "GLOBAL")
        environment: Environment (default: "production")
        config: Optional SDK configuration
    
    Returns:
        Tuple of (SignalResponse if sent, was_suppressed)
    """
    # Convert log_data to dict if it's a string
    if isinstance(log_data, str):
        extract_result = extract_v2_text(log_data)
    else:
        extract_result = extract_v2_json(log_data)
    
    # Use same logic as API response
    return analyze_api_response(
        log_data,
        client,
        source=source,
        region=region,
        environment=environment,
        config=config,
    )


def format_response_for_logging(response: SignalResponse) -> Dict[str, Any]:
    """
    Format a SignalResponse for safe logging (no raw data).
    
    Args:
        response: SignalResponse from backend
    
    Returns:
        Dictionary safe for logging
    """
    return {
        "risk_level": response.risk_level,
        "signal": response.signal,
        "affected_data_classes": response.affected_data_classes,
        "environment": response.context.get("environment"),
        "region": response.context.get("region"),
        "explanation": response.explanation,
    }

