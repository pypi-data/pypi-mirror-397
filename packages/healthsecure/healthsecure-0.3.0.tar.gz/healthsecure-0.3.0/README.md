# HealthSecure

**HealthSecure** is a runtime sensitive data exposure detection library for APIs and LLM outputs.

It helps engineering teams detect when **sensitive data** (medical, financial, credentials, personal identifiers) is unintentionally exposed in **production responses**, without sending raw data outside their systems.

HealthSecure analyzes responses **locally**, generates **privacy-preserving risk signals**, and sends only metadata to a centralized risk engine. Raw content is never stored or transmitted.

---

## Why HealthSecure

Modern applications increasingly rely on:

- APIs returning user data

- LLMs generating dynamic responses

- Logs and services emitting free-text output

Sensitive data leaks often happen **at runtime**, after:

- schema design

- code review

- static analysis

- compliance documentation

HealthSecure provides visibility where traditional tools fail:

**in live outputs, not in databases or schemas**.

---

## How It Works

### 1. Local Analysis (SDK)

- Inspects API or LLM responses in memory

- Detects sensitive data patterns using schema-agnostic heuristics

- Discards raw data immediately

### 2. Signal Generation

- Produces a minimal, irreversible signal describing:

  - detected data classes

  - identifiability

  - confidence

  - environment and region

### 3. Risk Evaluation

- Applies deterministic risk policy

- Returns a clear risk level: `LOW`, `MEDIUM`, or `HIGH`

- Backend never processes raw content

---

## Key Principles

- No raw data ingestion

- Schema-agnostic detection

- Deterministic and explainable behavior

- SDK-first design

- Privacy-by-design

- Production-focused

---

## Supported Data Classes

- Medical data

- Financial data

- Credentials (API keys, tokens, secrets)

- Personal identifiers (email, phone)

## v2 Features

- **Confidence Bands**: Automatic mapping of confidence scores to LOW/MEDIUM/HIGH bands
- **Reason Codes**: Explainable detection reasons (MEDICAL_TERM, CREDENTIAL_PATTERN, EMAIL_PATTERN, etc.)
- **Signal Fingerprinting**: Privacy-safe hashing for deduplication
- **Policy Context**: Optional policy configuration (min_confidence, blocked_classes)
- **Execution Context**: Enhanced metadata (channel, mode, sdk_version)

---

## Typical Use Cases

- Detect accidental leakage in LLM responses

- Monitor API responses for sensitive exposure

- Catch credential leaks in logs or service outputs

- Add a runtime safety layer without refactoring systems

---

## What HealthSecure Does NOT Do

- Does not store or transmit raw data

- Does not guarantee regulatory compliance

- Does not interpret business schemas

- Does not perform audits or certifications

- Does not replace encryption or access control

HealthSecure is a **risk detection layer**, not a compliance authority.

---

## Installation

```bash
pip install healthsecure==0.3.0
```

Or upgrade from previous versions:

```bash
pip install --upgrade healthsecure
```

---

## Quick Example

```python
from healthsecure import extract_v2_json, build_v2_signal, HealthSecureClient

raw_response = {
    "message": "API token leaked: sk_live_ABC123",
    "status": "error"
}

# v2 extraction with reason codes and confidence bands
extract = extract_v2_json(raw_response)
# Returns: detected_data_classes, identifiers_present, confidence,
#          confidence_band, reasons

# Build v2 signal with enhanced metadata
signal = build_v2_signal(
    extract,
    source="api_response",
    region="EU",
    environment="production"
)
# Signal includes: fingerprint, confidence_band, reasons

client = HealthSecureClient(api_key="YOUR_API_KEY")
result = client.analyze_signal(signal)

print(f"Risk: {result.risk_level}")
print(f"Reasons: {signal.reasons}")
print(f"Confidence Band: {signal.confidence_band}")
```

---

## Killer Demo: Safe LLM Wrapper

**Instant relevance for AI teams** - Wrap your LLM calls to detect sensitive data leakage:

```python
from healthsecure import safe_llm_call

# Wrap any LLM response
response, risk = safe_llm_call(
    "Patient John Doe (john@hospital.com) was diagnosed with HIV"
)

if risk == "HIGH":
    print("⚠️  Sensitive data detected! Blocking response.")
    # Block or sanitize response
else:
    print("✅ Response safe to return")
```

**See full example**: `example-app/safe_llm_call.py`

---

## API Reference

#### `extract_v2_json(raw: Any) -> Dict[str, Any]`

v2 extraction for JSON payloads with reason codes. Returns:

- `detected_data_classes`: List of data classes
- `identifiers_present`: Boolean
- `confidence`: Float (0.0-1.0)
- `confidence_band`: "LOW", "MEDIUM", or "HIGH"
- `reasons`: Sorted list of reason codes

#### `extract_v2_text(text: str) -> Dict[str, Any]`

v2 extraction for text payloads. Same return format as `extract_v2_json`.

#### `build_v2_signal(extract_result: Dict, *, source: str, region: str, environment: str, ...) -> SignalPayload`

Build a v2 SignalPayload from extraction results. Automatically includes:

- Confidence band mapping
- Reason codes
- Privacy-safe fingerprint
- Optional policy and execution context

### Helper Functions

#### `safe_llm_call(llm_response: str, ...) -> Tuple[str, str]`

Wrapper for LLM responses that detects sensitive data leakage. Returns `(response, risk_level)` where risk_level is "LOW", "MEDIUM", or "HIGH".

#### `HealthSecureClient.analyze_signal(payload: SignalPayload) -> SignalResponse`

Send signal to backend for risk assessment. Returns risk level (LOW/MEDIUM/HIGH) and explanation. Accepts both v1 and v2 signals.

---

## Risk Assessment Logic

- **HIGH Risk**:
  - Credentials detected in production (inherently high-risk)
  - Medical/biometric/children data + identifiers in production
- **MEDIUM Risk**:
  - Identifiers present with other sensitive data
  - Sensitive data in staging/development
- **LOW Risk**:
  - No identifiers, no high-risk classes

---

## Detection Limits

### Heuristic-Based Detection

HealthSecure uses **values-only extraction with format-based pattern detection**, not machine learning or schema understanding:

- ✅ **High-confidence signals**: Detects obvious sensitive data (API keys, credentials, medical terms, identifiers)
- ✅ **Reduced false positives**: Values-only scanning eliminates config/orchestration noise
- ✅ **Format-based credentials**: Only matches known secret formats, not keywords
- ⚠️ **Best-effort coverage**: May miss context-dependent or obfuscated data
- ⚠️ **No semantic understanding**: Cannot distinguish between "patient" (medical) and "patient" (waiting)

### Supported Detection Patterns

- **Medical**: Keywords (hiv, cancer, diabetes, diagnosis, treatment, medical, patient, disease, hypertension, medication, prescription, symptom)
- **Financial**: Keywords (credit card, debit card, ssn, social security, account number, routing number, iban, account balance, transaction amount)
- **Credentials**: Format-based detection (Stripe keys: `sk_live_*`, `sk_test_*`, Google API keys: `AIzaSy*`, AWS keys: `AKIA*`, JWT tokens: `Bearer eyJ*`, high-entropy secrets)
- **Personal Identifiers**: Email addresses (validated domain + TLD), phone numbers (formatted)

### What Gets Detected

✅ API keys (format-based: Stripe `sk_live_*`, `sk_test_*`, Google `AIzaSy*`, AWS `AKIA*`)  
✅ JWT tokens (`Bearer eyJ*` format)  
✅ High-entropy secrets (40+ character alphanumeric strings)  
✅ Email addresses (validated domain + TLD)  
✅ Phone numbers (formatted patterns)  
✅ Medical keywords in text values  
✅ Financial keywords in text values

### What May Be Missed

⚠️ Encrypted or encoded data  
⚠️ Context-dependent sensitive information  
⚠️ Industry-specific terminology not in keyword set  
⚠️ Structured data in non-standard formats

---

## Key Features (0.3.0)

- **Values-only extraction**: Only scans string values, never keys or field names
- **Orchestration path ignore**: System and workflow metadata paths are hard-ignored
- **Format-only credential detection**: Relies on known secret formats, not keywords
- **Hardened email detection**: Requires valid domain and TLD
- **Confidence bands**: LOW, MEDIUM, HIGH confidence levels
- **Reason codes**: Explainable detection reasons
- **Privacy-safe fingerprints**: Signal deduplication without content exposure
- **Policy and execution context**: Optional metadata for transparency

---

## Target Users

- Backend engineers

- AI / LLM engineers

- Platform and security teams

- Startups and SaaS teams running production APIs

---

## Requirements

- Python >= 3.9
- requests >= 2.31.0
- pydantic >= 2.0.0

---

## Project Status

- Version: `0.3.0` (stable)
- SDKs: Python (Node.js planned)
- Backend API: Stable v1 (accepts v2 signals)
- License: _(add license here)_

## What's New in 0.3.0

- ✨ Values-only extraction (eliminates false positives from config/orchestration data)
- ✨ Hardened detection patterns (format-only credentials, validated emails)
- ✨ Structural signals downgraded (context only, never elevate risk alone)
- ✨ Refined confidence scoring (clearer confidence bands)
- ✨ Regression test coverage (prevents future noise regressions)
- ✅ Drop-in replacement (no breaking changes)

---

## One-Line Summary

**HealthSecure detects sensitive data leaks in API and LLM outputs at runtime—without ever seeing your data.**

---

## Support

For issues, questions, or contributions, please [open an issue](link-to-issues).
