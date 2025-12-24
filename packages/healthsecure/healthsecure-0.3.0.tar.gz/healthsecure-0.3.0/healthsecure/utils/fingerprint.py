"""
Privacy-safe signal fingerprinting utility.
CRITICAL FIX FOR 0.3.0: Deterministic fingerprints
- Same semantic payload → same fingerprint
- Order-independent (dict key ordering doesn't matter)
"""

import hashlib
import json
from typing import Any, Dict


def _normalize_for_fingerprint(value: Any) -> Any:
    """
    Normalize a value for fingerprinting (order-independent, deterministic).
    
    This ensures:
    - Dict key ordering doesn't change fingerprint
    - List ordering matters (different order = different data)
    - None/null normalized
    """
    if value is None:
        return None
    
    if isinstance(value, dict):
        # Sort keys for deterministic ordering
        return {
            k: _normalize_for_fingerprint(v)
            for k, v in sorted(value.items())
        }
    
    if isinstance(value, list):
        # Lists preserve order (order matters for data)
        return [_normalize_for_fingerprint(item) for item in value]
    
    if isinstance(value, (int, float, bool, str)):
        return value
    
    # For other types, convert to string representation
    return str(value)


def fingerprint_signal(signal_dict: Dict[str, Any]) -> str:
    """
    Generate a privacy-safe fingerprint for a signal.
    
    CRITICAL FIX FOR 0.3.0:
    - Deterministic: Same semantic payload → same fingerprint
    - Order-independent: Dict key ordering doesn't matter
    - Privacy-safe: Only uses metadata, never raw data
    
    Args:
        signal_dict: Signal payload as dictionary
    
    Returns:
        SHA256 hash string (hex)
    """
    # Create a normalized copy for fingerprinting
    # Only include fields that matter for deduplication
    fingerprint_fields = {
        "signal_type": signal_dict.get("signal_type"),
        "source": signal_dict.get("source"),
        "detected_data_classes": sorted(signal_dict.get("detected_data_classes", [])),
        "identifiers_present": signal_dict.get("identifiers_present"),
        "confidence_band": signal_dict.get("confidence_band"),
        "reasons": sorted(signal_dict.get("reasons", [])),
        "region": signal_dict.get("region"),
        "environment": signal_dict.get("environment"),
        # Explicitly EXCLUDE:
        # - timestamp (changes every time)
        # - confidence (numeric, may vary slightly)
        # - fingerprint itself (circular)
        # - policy/context (may vary but same signal)
    }
    
    # Normalize for deterministic hashing
    normalized = _normalize_for_fingerprint(fingerprint_fields)
    
    # Convert to JSON string (sorted keys)
    json_str = json.dumps(normalized, sort_keys=True, separators=(',', ':'))
    
    # Generate SHA256 hash
    hash_obj = hashlib.sha256(json_str.encode('utf-8'))
    
    return f"sha256:{hash_obj.hexdigest()}"
