"""
Helper functions for building v2 signals.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any

from healthsecure.types import SignalPayload, PolicyContext, ExecutionContextV2
from healthsecure.utils.fingerprint import fingerprint_signal


def build_v2_signal(
    extract_result: Dict[str, Any],
    *,
    source: str,
    region: str,
    environment: str,
    policy: Optional[PolicyContext] = None,
    context: Optional[ExecutionContextV2] = None,
) -> SignalPayload:
    """
    Build a v2 SignalPayload from extraction results.
    
    Args:
        extract_result: Result from extract_v2_json() or extract_v2_text()
        source: Signal source (e.g., "llm_response", "api_response")
        region: Region code (e.g., "EU", "US")
        environment: Environment (e.g., "production", "staging")
        policy: Optional policy context
        context: Optional execution context v2
    
    Returns:
        SignalPayload with v2 fields populated
    """
    signal = SignalPayload(
        signal_type="OUTPUT_EXPOSURE",
        source=source,
        detected_data_classes=extract_result["detected_data_classes"] or ["personal"],
        identifiers_present=extract_result["identifiers_present"],
        confidence=extract_result["confidence"],
        confidence_band=extract_result.get("confidence_band"),
        reasons=extract_result.get("reasons"),
        region=region,
        environment=environment,
        policy=policy,
        context_v2=context,
        timestamp=datetime.now(timezone.utc),
    )
    
    # Generate fingerprint after signal is created
    signal.fingerprint = fingerprint_signal(signal.model_dump())
    
    return signal

