import re
from typing import Set, Tuple


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


def extract_from_text(text: str) -> Tuple[Set[str], bool, float]:
    """
    Analyze raw text locally (e.g. LLM output).

    This function never makes HTTP calls, logs data, or stores anything.
    Raw text never leaves this function.
    
    FROZEN FOR V1 - Detection logic is locked.
    """

    classes: Set[str] = set()
    identifiers: Set[str] = set()

    text_lower = text.lower()

    # identifiers
    if EMAIL_REGEX.search(text) or PHONE_REGEX.search(text):
        identifiers.add("personal")

    # medical
    if any(k in text_lower for k in MEDICAL_KEYWORDS):
        classes.add("medical")

    # financial
    if any(k in text_lower for k in FINANCIAL_KEYWORDS):
        classes.add("financial")

    # credentials
    if any(k in text_lower for k in CREDENTIAL_KEYWORDS) or TOKEN_REGEX.search(text):
        classes.add("credentials")

    identifiers_present = bool(identifiers)

    if classes and identifiers_present:
        confidence = 0.95
    elif classes:
        confidence = 0.75
    else:
        confidence = 0.3

    return classes, identifiers_present, confidence
