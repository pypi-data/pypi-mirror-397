import re
from typing import Any, Set, Tuple, Dict


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


def _walk(value: Any, classes: Set[str], identifiers: Set[str]) -> None:
    """
    Recursively walk nested dicts and lists to detect sensitive data.
    FROZEN FOR V1 - Do not modify detection logic.
    """
    if isinstance(value, dict):
        for v in value.values():
            _walk(v, classes, identifiers)

    elif isinstance(value, list):
        for item in value:
            _walk(item, classes, identifiers)

    elif isinstance(value, str):
        text = value.lower()

        # identifiers
        if EMAIL_REGEX.search(value) or PHONE_REGEX.search(value):
            identifiers.add("personal")

        # medical
        if any(k in text for k in MEDICAL_KEYWORDS):
            classes.add("medical")

        # financial
        if any(k in text for k in FINANCIAL_KEYWORDS):
            classes.add("financial")

        # credentials
        if any(k in text for k in CREDENTIAL_KEYWORDS) or TOKEN_REGEX.search(value):
            classes.add("credentials")


def extract_from_json(payload: Dict[str, Any]) -> Tuple[Set[str], bool, float]:
    """
    Analyze raw JSON locally and return:
    - detected_data_classes (medical, financial, credentials)
    - identifiers_present (personal identifiers detected)
    - confidence

    This function never makes HTTP calls, logs data, or stores anything.
    Raw payload never leaves this function.
    Recursively walks nested structures.
    
    FROZEN FOR V1 - Detection logic is locked.
    """

    classes: Set[str] = set()
    identifiers: Set[str] = set()

    _walk(payload, classes, identifiers)

    identifiers_present = bool(identifiers)

    if classes and identifiers_present:
        confidence = 0.95
    elif classes:
        confidence = 0.75
    else:
        confidence = 0.3

    return classes, identifiers_present, confidence
