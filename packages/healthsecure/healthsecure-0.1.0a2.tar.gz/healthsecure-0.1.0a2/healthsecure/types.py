from typing import List, Literal, Annotated
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
Environment = Literal["production", "staging", "development"]


class SignalPayload(BaseModel):
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

    model_config = ConfigDict(extra="forbid")


class SignalResponse(BaseModel):
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    signal: Literal["SENSITIVE_DATA_EXPOSED"]
    affected_data_classes: List[str]
    context: dict
    explanation: str

