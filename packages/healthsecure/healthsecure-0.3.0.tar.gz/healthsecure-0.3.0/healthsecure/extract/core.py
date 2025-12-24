"""
Core extraction logic with v2 reason tracking.
CRITICAL FIX FOR 0.3.0: VALUES-ONLY SCANNING
- Only scan string VALUES, never keys/field names
- Ignore config/orchestration paths
- Tightened regex patterns
"""

import re
from typing import Any, Set, Tuple, List

from healthsecure.constants import (
    MEDICAL_TERM,
    FINANCIAL_TERM,
    CREDENTIAL_PATTERN,
    EMAIL_PATTERN,
    PHONE_PATTERN,
    FREE_TEXT_EXPOSURE,
    NESTED_PAYLOAD,
)

# ============================================================================
# IGNORED PATHS (Config/Orchestration Metadata)
# ============================================================================
# These paths are NEVER scanned - they are schema/config, not data
IGNORED_PATH_PATTERNS = [
    r"^config\.",  # All config paths
    r"\.nodes\.",  # Workflow nodes
    r"^inputs\.",  # Input definitions
    r"^outputs\.",  # Output definitions
    r"\.edges\.",  # Graph edges
    r"\.template_id$",
    r"\.subtype_id$",
    r"\.process_id$",
    r"\.icon_",
    r"\.node_id$",
    r"\.index$",
    r"\.position$",
    r"\.connection_position$",
    r"\.next$",
    r"\.id$",  # Generic IDs (not PII)
    r"^_id$",  # MongoDB-style IDs
    r"\.type$",  # Type fields (not data)
    r"\.data_type$",
    r"\.input_type$",
    r"\.output_type$",
    r"\.value_from$",
    r"\.option_values$",
    r"\.option_names$",
    r"\.description$",  # Descriptions are metadata
    r"\.name$",  # Field names (not values)
    r"\.label$",
    r"\.icon_name$",
    r"\.icon_color$",
    r"\.animated$",
    r"\.custom_types$",
    r"\.trigger$",
    r"\.map_parameter_value$",  # Orchestration metadata
    r"\.map_parameter$",
    r"^updated_at$",
    r"^last_run_at$",
    r"^created_at$",
]

IGNORED_PATTERNS_COMPILED = [re.compile(pattern, re.IGNORECASE) for pattern in IGNORED_PATH_PATTERNS]


def is_ignored_path(path: str) -> bool:
    """
    Check if a JSON path should be ignored (config/schema, not data).
    
    Args:
        path: JSON path like "config.nodes.0.inputs.0.name"
    
    Returns:
        True if path should be ignored
    """
    for pattern in IGNORED_PATTERNS_COMPILED:
        if pattern.search(path):
            return True
    return False


# ============================================================================
# TIGHTENED REGEX PATTERNS (0.3.0 FIX)
# ============================================================================

# Email: Must have real domain + TLD (no @\S+)
EMAIL_REGEX = re.compile(
    r"\b[a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?@[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?\.[a-zA-Z]{2,}\b"
)

# Phone: More strict (10-15 digits, with optional formatting)
PHONE_REGEX = re.compile(
    r"\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b"
)

# Credentials: Match FORMATS only, not keywords
# Must look like actual secrets with known prefixes or high entropy
CREDENTIAL_FORMAT_REGEX = re.compile(
    r"\b(?:"
    r"sk_live_[A-Za-z0-9]{20,}|"  # Stripe live keys
    r"sk_test_[A-Za-z0-9]{20,}|"  # Stripe test keys
    r"api_key_[A-Za-z0-9]{20,}|"  # Generic API keys
    r"AIzaSy[A-Za-z0-9_-]{35,}|"  # Google API keys
    r"AKIA[0-9A-Z]{16,}|"  # AWS access keys
    r"Bearer\s+eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}(?:\.[A-Za-z0-9_-]{10,})?|"  # Bearer JWT tokens
    r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}(?:\.[A-Za-z0-9_-]{10,})?|"  # JWT tokens
    r"[A-Za-z0-9]{40,}"  # Long alphanumeric strings (high entropy, likely secrets)
    r")\b"
)

# Medical keywords (only in VALUES, not keys)
MEDICAL_KEYWORDS = {
    "hiv", "cancer", "diabetes", "diagnosed",
    "diagnosis", "treatment", "medical",
    "patient", "disease", "hypertension",
    "medication", "prescription", "symptom"
}

# Financial keywords (only in VALUES, not keys)
FINANCIAL_KEYWORDS = {
    "credit card", "debit card", "ssn", "social security",
    "account number", "routing number", "iban",
    "account balance", "transaction amount"
}


# ============================================================================
# VALUES-ONLY WALKING (CRITICAL FIX)
# ============================================================================

def walk_v2(
    value: Any,
    classes: Set[str],
    identifiers: Set[str],
    reasons: Set[str],
    current_path: str = "",
) -> None:
    """
    Recursively walk nested dicts and lists to detect sensitive data.
    
    CRITICAL: Only scans VALUES, never keys/field names.
    
    Args:
        value: Value to analyze (dict, list, or str)
        classes: Set to accumulate detected data classes
        identifiers: Set to accumulate identifier types
        reasons: Set to accumulate reason codes
        current_path: Current JSON path (for ignoring config paths)
    """
    if isinstance(value, dict):
        # Check if this path should be ignored
        if current_path and is_ignored_path(current_path):
            return  # Skip entire subtree
        
        # ONLY iterate over VALUES, never check keys
        for key, val in value.items():
            # Build path for ignore checking
            next_path = f"{current_path}.{key}" if current_path else key
            
            # Skip if path is ignored
            if is_ignored_path(next_path):
                continue  # Skip this key-value pair entirely
            
            # Recursively walk the VALUE only
            walk_v2(val, classes, identifiers, reasons, next_path)

    elif isinstance(value, list):
        # For lists, check path but walk all items
        if current_path and is_ignored_path(current_path):
            return  # Skip entire list
        
        # Track if we detect anything in this list
        classes_before = len(classes)
        identifiers_before = len(identifiers)
        
        for idx, item in enumerate(value):
            next_path = f"{current_path}[{idx}]" if current_path else f"[{idx}]"
            walk_v2(item, classes, identifiers, reasons, next_path)
        
        # Only add NESTED_PAYLOAD if we actually found something
        if len(classes) > classes_before or len(identifiers) > identifiers_before:
            reasons.add(NESTED_PAYLOAD)

    elif isinstance(value, str):
        # CRITICAL: Only scan string VALUES, never keys
        # current_path tells us if this is a value (we're here) or a key (we'd never be here for keys)
        
        text = value.lower()
        detected_anything = False

        # Email: Tightened pattern
        if EMAIL_REGEX.search(value):
            identifiers.add("personal")
            reasons.add(EMAIL_PATTERN)
            detected_anything = True

        # Phone: Tightened pattern
        if PHONE_REGEX.search(value):
            identifiers.add("personal")
            reasons.add(PHONE_PATTERN)
            detected_anything = True

        # Medical: Only check if value contains medical terms
        # (Not checking keys - we're in a string value)
        if any(kw in text for kw in MEDICAL_KEYWORDS):
            classes.add("medical")
            reasons.add(MEDICAL_TERM)
            detected_anything = True

        # Financial: Only check if value contains financial terms
        if any(kw in text for kw in FINANCIAL_KEYWORDS):
            classes.add("financial")
            reasons.add(FINANCIAL_TERM)
            detected_anything = True

        # Credentials: FORMAT-ONLY matching (no keyword matching)
        # Must look like actual secret formats
        if CREDENTIAL_FORMAT_REGEX.search(value):
            classes.add("credentials")
            reasons.add(CREDENTIAL_PATTERN)
            detected_anything = True
        
        # Only add structural reasons if we actually detected something
        # This prevents noise from empty/config strings
        if detected_anything:
            reasons.add(FREE_TEXT_EXPOSURE)


# ============================================================================
# LEGACY V1 WALK (FROZEN - for backward compatibility)
# ============================================================================

def _walk_legacy(value: Any, classes: Set[str], identifiers: Set[str]) -> None:
    """
    Legacy v1 walker (FROZEN - do not modify).
    Only used by extract_from_json for backward compatibility.
    """
    if isinstance(value, dict):
        for v in value.values():
            _walk_legacy(v, classes, identifiers)
    elif isinstance(value, list):
        for item in value:
            _walk_legacy(item, classes, identifiers)
    elif isinstance(value, str):
        text = value.lower()
        
        # Legacy patterns (kept for v1 compatibility)
        EMAIL_REGEX_LEGACY = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
        PHONE_REGEX_LEGACY = re.compile(r"\b\d{10,15}\b")
        
        if EMAIL_REGEX_LEGACY.search(value) or PHONE_REGEX_LEGACY.search(value):
            identifiers.add("personal")
        
        MEDICAL_KEYWORDS_LEGACY = {
            "hiv", "cancer", "diabetes", "diagnosed",
            "diagnosis", "treatment", "medical",
            "patient", "disease"
        }
        if any(k in text for k in MEDICAL_KEYWORDS_LEGACY):
            classes.add("medical")
        
        FINANCIAL_KEYWORDS_LEGACY = {
            "credit", "debit", "card", "iban",
            "account", "payment", "paid",
            "transaction", "billing"
        }
        if any(k in text for k in FINANCIAL_KEYWORDS_LEGACY):
            classes.add("financial")
        
        # Legacy credential check (keyword-based - kept for compatibility)
        CREDENTIAL_KEYWORDS_LEGACY = {
            "token", "api_key", "apikey",
            "secret", "password", "auth",
            "bearer", "sk_"
        }
        TOKEN_REGEX_LEGACY = re.compile(r"(sk_|api_|token|secret|password)", re.IGNORECASE)
        if any(k in text for k in CREDENTIAL_KEYWORDS_LEGACY) or TOKEN_REGEX_LEGACY.search(value):
            classes.add("credentials")
