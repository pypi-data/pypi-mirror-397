"""
Safe LLM wrapper that detects sensitive data leakage.

This is a killer demo for AI teams - wrap your LLM calls to detect sensitive data.
"""

from datetime import datetime, timezone
from typing import Tuple
from .client import HealthSecureClient
from .types import SignalPayload
from .extract import extract_from_text


def safe_llm_call(
    llm_response: str,
    api_key: str = "dev-secret-key",
    base_url: str = "http://localhost:8000",
    region: str = "EU",
    environment: str = "production"
) -> Tuple[str, str]:
    """
    Wrapper for LLM responses that detects sensitive data leakage.
    
    Args:
        llm_response: The LLM output text to analyze
        api_key: HealthSecure API key
        base_url: HealthSecure backend URL
        region: Region code (EU, US, IN, CN, GLOBAL)
        environment: Environment (production, staging, development)
    
    Returns:
        (response, risk_level) where risk_level is "LOW", "MEDIUM", or "HIGH"
    
    Example:
        response, risk = safe_llm_call("Patient diagnosed with HIV")
        if risk == "HIGH":
            print("⚠️  Sensitive data detected! Blocking response.")
    """
    # Extract signal locally (raw data never leaves your environment)
    classes, identifiers, confidence = extract_from_text(llm_response)
    
    # Build signal payload
    signal = SignalPayload(
        signal_type="OUTPUT_EXPOSURE",
        source="llm_response",
        detected_data_classes=list(classes) if classes else ["personal"],
        identifiers_present=identifiers,
        confidence=confidence,
        region=region,
        environment=environment,
        timestamp=datetime.now(timezone.utc)
    )
    
    # Send to backend for risk assessment
    client = HealthSecureClient(api_key=api_key, base_url=base_url)
    result = client.analyze_signal(signal)
    
    return llm_response, result.risk_level

