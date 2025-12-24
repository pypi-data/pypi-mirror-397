"""
Privacy-safe signal fingerprinting.
"""

import hashlib
import json
from typing import Dict, Any


def fingerprint_signal(signal_dict: Dict[str, Any]) -> str:
    """
    Generate a privacy-safe fingerprint for a signal.
    
    Excludes timestamp and fingerprint fields to ensure
    deterministic hashing of signal content.
    
    Args:
        signal_dict: Signal payload as dictionary
    
    Returns:
        SHA256 hash prefixed with "sha256:"
    """
    filtered = {
        k: v for k, v in signal_dict.items()
        if k not in {"timestamp", "fingerprint"}
    }
    payload = json.dumps(filtered, sort_keys=True, default=str).encode()
    return "sha256:" + hashlib.sha256(payload).hexdigest()

