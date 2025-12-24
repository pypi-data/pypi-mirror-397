from typing import List, Literal, Annotated, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


SignalType = Literal["OUTPUT_EXPOSURE"]
SignalSource = Literal["llm_response", "api_response", "service_response"]
DataClass = Literal[
    "medical",
    "financial",
    "biometric",
    "personal",
    "children",
    "credentials"
]
Region = Literal["EU", "US", "IN", "CN", "GLOBAL"]
Environment = Literal["production", "staging", "development", "ci", "preview"]

# v2 extensions
ConfidenceBand = Literal["LOW", "MEDIUM", "HIGH"]


class PolicyContext(BaseModel):
    """v2: Policy context for signal evaluation."""
    min_confidence: Optional[ConfidenceBand] = None
    blocked_classes: Optional[List[str]] = None


class ExecutionContextV2(BaseModel):
    """v2: Execution context metadata."""
    channel: Optional[Literal["api", "llm", "log", "ci"]] = None
    mode: Optional[Literal["blocking", "monitor"]] = None
    sdk_version: Optional[str] = None


class SignalPayload(BaseModel):
    # -------- v1 fields (unchanged) --------
    signal_type: SignalType
    source: SignalSource
    detected_data_classes: Annotated[
        List[DataClass],
        Field(min_length=1)
    ]
    identifiers_present: bool
    confidence: Annotated[float, Field(ge=0.0, le=1.0)]
    region: Region
    environment: Environment
    timestamp: datetime

    # -------- v2 extensions (optional) --------
    confidence_band: Optional[ConfidenceBand] = None
    reasons: Optional[List[str]] = None
    fingerprint: Optional[str] = None
    policy: Optional[PolicyContext] = None
    context_v2: Optional[ExecutionContextV2] = None

    model_config = ConfigDict(extra="forbid")


class SignalResponse(BaseModel):
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    signal: Literal["SENSITIVE_DATA_EXPOSED"]
    affected_data_classes: List[str]
    context: dict
    explanation: str

