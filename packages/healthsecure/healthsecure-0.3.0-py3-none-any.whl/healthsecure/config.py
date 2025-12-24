"""
SDK configuration for thresholds, blocked classes, and suppression.
"""

from typing import Optional, List, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict


@dataclass
class SDKConfig:
    """
    Configuration for HealthSecure SDK behavior.
    
    Attributes:
        min_confidence_band: Minimum confidence band to send signals (LOW, MEDIUM, HIGH)
        blocked_data_classes: Data classes that should be blocked (e.g., ["credentials"])
        suppression_window_hours: Hours to suppress duplicate signals by fingerprint
        enable_suppression: Whether to enable fingerprint-based suppression
    """
    min_confidence_band: Optional[str] = None  # "LOW", "MEDIUM", or "HIGH"
    blocked_data_classes: List[str] = field(default_factory=list)
    suppression_window_hours: int = 24
    enable_suppression: bool = True
    
    def should_block(self, data_classes: List[str]) -> bool:
        """Check if any detected data classes are blocked."""
        if not self.blocked_data_classes:
            return False
        return any(cls in self.blocked_data_classes for cls in data_classes)
    
    def should_send(self, confidence_band: Optional[str]) -> bool:
        """Check if signal meets minimum confidence threshold."""
        if not self.min_confidence_band:
            return True
        
        band_order = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
        min_level = band_order.get(self.min_confidence_band, 0)
        signal_level = band_order.get(confidence_band, 0)
        return signal_level >= min_level


class SuppressionStore:
    """
    In-memory store for fingerprint-based signal suppression.
    """
    
    def __init__(self, window_hours: int = 24):
        self.window_hours = window_hours
        self._store: defaultdict = defaultdict(list)  # fingerprint -> [timestamps]
    
    def is_suppressed(self, fingerprint: Optional[str]) -> bool:
        """Check if a fingerprint should be suppressed."""
        if not fingerprint:
            return False
        
        now = datetime.utcnow()
        cutoff = now - timedelta(hours=self.window_hours)
        
        # Clean old entries
        self._store[fingerprint] = [
            ts for ts in self._store[fingerprint]
            if ts > cutoff
        ]
        
        # Check if suppressed
        return len(self._store[fingerprint]) > 0
    
    def record(self, fingerprint: Optional[str]) -> None:
        """Record a fingerprint for suppression."""
        if fingerprint:
            self._store[fingerprint].append(datetime.utcnow())
    
    def clear(self) -> None:
        """Clear all suppression records."""
        self._store.clear()


# Global default config
_default_config = SDKConfig()
_default_suppression = SuppressionStore()


def get_default_config() -> SDKConfig:
    """Get the default SDK configuration."""
    return _default_config


def get_default_suppression() -> SuppressionStore:
    """Get the default suppression store."""
    return _default_suppression

