"""
v2 extraction API with reason codes and confidence bands.
"""

from typing import Any, Dict

from healthsecure.extract.core import walk_v2
from healthsecure.utils.confidence import confidence_to_band


def extract_v2_json(raw: Any) -> Dict[str, Any]:
    """
    v2 extraction for JSON payloads with reason codes.
    
    Returns a dictionary with:
    - detected_data_classes: List of data classes
    - identifiers_present: Boolean
    - confidence: Float (0.0-1.0)
    - confidence_band: "LOW", "MEDIUM", or "HIGH"
    - reasons: Sorted list of reason codes
    
    Args:
        raw: JSON payload (dict, list, or any nested structure)
    
    Returns:
        Dictionary with extraction results including v2 fields
    """
    classes: set = set()
    identifiers: set = set()
    reasons: set = set()
    
    walk_v2(raw, classes, identifiers, reasons)
    
    identifiers_present = bool(identifiers)
    
    if classes and identifiers_present:
        confidence = 0.95
    elif classes:
        confidence = 0.75
    else:
        confidence = 0.3
    
    return {
        "detected_data_classes": list(classes),
        "identifiers_present": identifiers_present,
        "confidence": confidence,
        "confidence_band": confidence_to_band(confidence),
        "reasons": sorted(reasons),
    }


def extract_v2_text(text: str) -> Dict[str, Any]:
    """
    v2 extraction for text payloads with reason codes.
    
    Same return format as extract_v2_json.
    
    Args:
        text: Plain text string to analyze
    
    Returns:
        Dictionary with extraction results including v2 fields
    """
    # Convert text to a simple structure for walk_v2
    # This ensures consistent reason tracking
    classes: set = set()
    identifiers: set = set()
    reasons: set = set()
    
    walk_v2(text, classes, identifiers, reasons)
    
    identifiers_present = bool(identifiers)
    
    if classes and identifiers_present:
        confidence = 0.95
    elif classes:
        confidence = 0.75
    else:
        confidence = 0.3
    
    return {
        "detected_data_classes": list(classes),
        "identifiers_present": identifiers_present,
        "confidence": confidence,
        "confidence_band": confidence_to_band(confidence),
        "reasons": sorted(reasons),
    }

