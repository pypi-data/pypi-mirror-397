"""
Confidence band mapping utilities.
"""


def confidence_to_band(confidence: float) -> str:
    """
    Map confidence score to confidence band.
    
    Args:
        confidence: Float between 0.0 and 1.0
    
    Returns:
        "LOW", "MEDIUM", or "HIGH"
    """
    if confidence < 0.5:
        return "LOW"
    if confidence < 0.8:
        return "MEDIUM"
    return "HIGH"

