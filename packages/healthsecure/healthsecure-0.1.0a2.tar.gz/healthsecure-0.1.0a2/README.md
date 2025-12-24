# HealthSecure

**HealthSecure** is a runtime sensitive data exposure detection library for APIs and LLM outputs.

It helps engineering teams detect when **sensitive data** (medical, financial, credentials, personal identifiers) is unintentionally exposed in **production responses**, without sending raw data outside their systems.

HealthSecure analyzes responses **locally**, generates **privacy-preserving risk signals**, and sends only metadata to a centralized risk engine. Raw content is never stored or transmitted.

---

## Why HealthSecure

Modern applications increasingly rely on:

* APIs returning user data

* LLMs generating dynamic responses

* Logs and services emitting free-text output

Sensitive data leaks often happen **at runtime**, after:

* schema design

* code review

* static analysis

* compliance documentation

HealthSecure provides visibility where traditional tools fail:

**in live outputs, not in databases or schemas**.

---

## How It Works

### 1. Local Analysis (SDK)

* Inspects API or LLM responses in memory

* Detects sensitive data patterns using schema-agnostic heuristics

* Discards raw data immediately

### 2. Signal Generation

* Produces a minimal, irreversible signal describing:

  * detected data classes

  * identifiability

  * confidence

  * environment and region

### 3. Risk Evaluation

* Applies deterministic risk policy

* Returns a clear risk level: `LOW`, `MEDIUM`, or `HIGH`

* Backend never processes raw content

---

## Key Principles

* No raw data ingestion

* Schema-agnostic detection

* Deterministic and explainable behavior

* SDK-first design

* Privacy-by-design

* Production-focused

---

## Supported Data Classes (v1)

* Medical data

* Financial data

* Credentials (API keys, tokens, secrets)

* Personal identifiers (email, phone)

---

## Typical Use Cases

* Detect accidental leakage in LLM responses

* Monitor API responses for sensitive exposure

* Catch credential leaks in logs or service outputs

* Add a runtime safety layer without refactoring systems

---

## What HealthSecure Does NOT Do

* Does not store or transmit raw data

* Does not guarantee regulatory compliance

* Does not interpret business schemas

* Does not perform audits or certifications

* Does not replace encryption or access control

HealthSecure is a **risk detection layer**, not a compliance authority.

---

## Installation

```bash
pip install healthsecure==0.1.0a1
```

---

## Quick Example

```python
from healthsecure import extract_from_json, HealthSecureClient, SignalPayload
from datetime import datetime, timezone

raw_response = {
    "message": "API token leaked: sk_live_ABC123",
    "status": "error"
}

classes, identifiers, confidence = extract_from_json(raw_response)

signal = SignalPayload(
    signal_type="OUTPUT_EXPOSURE",
    source="api_response",
    detected_data_classes=list(classes),
    identifiers_present=identifiers,
    confidence=confidence,
    region="EU",
    environment="production",
    timestamp=datetime.now(timezone.utc)
)

client = HealthSecureClient(api_key="YOUR_API_KEY")
result = client.analyze_signal(signal)

print(result)
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

### `extract_from_json(payload: Dict[str, Any]) -> Tuple[Set[str], bool, float]`

Analyze raw JSON locally. Returns:
- `detected_classes`: Set of data classes found (medical, financial, credentials)
- `identifiers_present`: Boolean indicating if personal identifiers were detected
- `confidence`: Float (0.0-1.0) indicating detection confidence

### `extract_from_text(text: str) -> Tuple[Set[str], bool, float]`

Analyze raw text (e.g., LLM output). Same return format as `extract_from_json`.

### `safe_llm_call(llm_response: str, ...) -> Tuple[str, str]`

Wrapper for LLM responses that detects sensitive data leakage. Returns `(response, risk_level)` where risk_level is "LOW", "MEDIUM", or "HIGH".

### `HealthSecureClient.analyze_signal(payload: SignalPayload) -> SignalResponse`

Send signal to backend for risk assessment. Returns risk level (LOW/MEDIUM/HIGH) and explanation.

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

HealthSecure uses **keyword matching and pattern detection**, not machine learning or schema understanding:

- ✅ **High-confidence signals**: Detects obvious sensitive data (credit cards, API keys, medical terms)
- ⚠️ **Best-effort coverage**: May miss context-dependent or obfuscated data
- ⚠️ **False positives possible**: Generic terms may trigger false alarms
- ⚠️ **No semantic understanding**: Cannot distinguish between "patient" (medical) and "patient" (waiting)

### Supported Detection Patterns

- **Medical**: 9 keywords (hiv, cancer, diabetes, diagnosis, treatment, medical, patient, disease, diagnosed)
- **Financial**: 9 keywords (credit, debit, card, iban, account, payment, paid, transaction, billing)
- **Credentials**: 8 keywords (token, api_key, apikey, secret, password, auth, bearer, sk_)
- **Personal Identifiers**: Email addresses (regex), phone numbers (regex)

### What Gets Detected

✅ Credit card numbers (pattern matching)  
✅ API keys (pattern matching: sk_, pk_, api_)  
✅ Email addresses (regex)  
✅ Medical keywords in text  
✅ Financial keywords in text  
✅ Credential keywords in text  

### What May Be Missed

⚠️ Encrypted or encoded data  
⚠️ Context-dependent sensitive information  
⚠️ Industry-specific terminology not in keyword set  
⚠️ Structured data in non-standard formats  

---

## Stability & Contracts

**v1 contracts are frozen** - See [STABILITY.md](STABILITY.md) for:
- Locked signal schema
- Frozen risk policy table
- Documented extractor limitations
- Versioning strategy

---

## Target Users

* Backend engineers

* AI / LLM engineers

* Platform and security teams

* Startups and SaaS teams running production APIs

---

## Requirements

- Python >= 3.9
- requests >= 2.31.0
- pydantic >= 2.0.0

---

## Project Status

* Version: `0.1.0a1` (alpha)
* SDKs: Python (Node.js planned)
* Backend API: Stable v1
* License: *(add license here)*

---

## One-Line Summary

**HealthSecure detects sensitive data leaks in API and LLM outputs at runtime—without ever seeing your data.**

---

## Support

For issues, questions, or contributions, please [open an issue](link-to-issues).
