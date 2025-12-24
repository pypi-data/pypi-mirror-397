"""
Core extraction logic with v2 reason tracking.
"""

import re
from typing import Any, Set, Dict

from healthsecure.constants import (
    MEDICAL_TERM,
    FINANCIAL_TERM,
    CREDENTIAL_PATTERN,
    EMAIL_PATTERN,
    PHONE_PATTERN,
    FREE_TEXT_EXPOSURE,
    NESTED_PAYLOAD,
)

# Shared regex patterns
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_REGEX = re.compile(r"\b\d{10,15}\b")
TOKEN_REGEX = re.compile(r"(sk_|api_|token|secret|password)", re.IGNORECASE)

MEDICAL_KEYWORDS = {
    "hiv", "cancer", "diabetes", "diagnosed",
    "diagnosis", "treatment", "medical",
    "patient", "disease"
}

FINANCIAL_KEYWORDS = {
    "credit", "debit", "card", "iban",
    "account", "payment", "paid",
    "transaction", "billing"
}

CREDENTIAL_KEYWORDS = {
    "token", "api_key", "apikey",
    "secret", "password", "auth",
    "bearer", "sk_"
}


def walk_v2(value: Any, classes: Set[str], identifiers: Set[str], reasons: Set[str]) -> None:
    """
    Recursively walk nested dicts and lists to detect sensitive data (v2 with reasons).
    
    Args:
        value: Value to analyze (dict, list, or str)
        classes: Set to accumulate detected data classes
        identifiers: Set to accumulate identifier types
        reasons: Set to accumulate reason codes
    """
    if isinstance(value, dict):
        reasons.add(NESTED_PAYLOAD)
        for v in value.values():
            walk_v2(v, classes, identifiers, reasons)

    elif isinstance(value, list):
        reasons.add(NESTED_PAYLOAD)
        for item in value:
            walk_v2(item, classes, identifiers, reasons)

    elif isinstance(value, str):
        text = value.lower()
        reasons.add(FREE_TEXT_EXPOSURE)

        # identifiers
        if EMAIL_REGEX.search(value):
            identifiers.add("personal")
            reasons.add(EMAIL_PATTERN)

        if PHONE_REGEX.search(value):
            identifiers.add("personal")
            reasons.add(PHONE_PATTERN)

        # medical
        if any(k in text for k in MEDICAL_KEYWORDS):
            classes.add("medical")
            reasons.add(MEDICAL_TERM)

        # financial
        if any(k in text for k in FINANCIAL_KEYWORDS):
            classes.add("financial")
            reasons.add(FINANCIAL_TERM)

        # credentials
        if any(k in text for k in CREDENTIAL_KEYWORDS) or TOKEN_REGEX.search(value):
            classes.add("credentials")
            reasons.add(CREDENTIAL_PATTERN)

