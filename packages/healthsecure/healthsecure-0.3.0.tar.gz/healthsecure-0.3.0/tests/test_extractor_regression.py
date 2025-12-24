"""
Regression tests for extractor (STEP 6 - MANDATORY).

These tests ensure workflow/config JSON produces LOW risk,
while real sensitive data produces HIGH risk.
"""

import pytest
from healthsecure.extract.v2 import extract_v2_json


# ============================================================================
# MUST BE LOW (Workflow/Config JSON)
# ============================================================================

def test_workflow_config_json():
    """Workflow config JSON should produce LOW risk."""
    workflow_json = {
        "_id": "68e8901ffdb8e63494cf5f93",
        "name": "Marine Insurance Underwriting",
        "is_active": True,
        "process_id": "68e4fc9f9b632c1f3fbc09b8",
        "config": {
            "nodes": [
                {
                    "id": "1",
                    "type": "start",
                    "name": "Start",
                    "inputs": [
                        {
                            "name": "api_key",
                            "type": "workflow",
                            "data_type": "string"
                        }
                    ]
                }
            ],
            "edges": [
                {
                    "source": "node_1",
                    "target": "2",
                    "type": "custom-edge"
                }
            ]
        },
        "updated_at": "2025-11-21 06:19:29.094000"
    }
    
    result = extract_v2_json(workflow_json)
    
    assert result["confidence_band"] == "LOW", f"Expected LOW, got {result['confidence_band']}"
    assert len(result["detected_data_classes"]) == 0, "Should not detect data classes in config"
    assert result["identifiers_present"] == False, "Should not detect identifiers in config"


def test_ci_pipeline_config():
    """CI pipeline config should produce LOW risk."""
    ci_config = {
        "pipeline": {
            "steps": [
                {
                    "name": "build",
                    "script": "npm run build",
                    "env": {
                        "NODE_ENV": "production",
                        "API_URL": "https://api.example.com"
                    }
                }
            ],
            "secrets": {
                "api_key": "${CI_API_KEY}"
            }
        }
    }
    
    result = extract_v2_json(ci_config)
    
    assert result["confidence_band"] == "LOW", f"Expected LOW, got {result['confidence_band']}"
    assert len(result["detected_data_classes"]) == 0, "Should not detect data classes in CI config"


def test_llm_orchestration_metadata():
    """LLM orchestration metadata should produce LOW risk."""
    llm_metadata = {
        "template_id": "685e5882c24f17afc1be8d37",
        "subtype_id": "68835226a81bff639ce8a69e",
        "node_id": "4",
        "inputs": [
            {
                "name": "prompt",
                "type": "workflow",
                "data_type": "string",
                "value_from": "user"
            }
        ],
        "outputs": [
            {
                "name": "response",
                "type": "execution",
                "data_type": "dict"
            }
        ]
    }
    
    result = extract_v2_json(llm_metadata)
    
    assert result["confidence_band"] == "LOW", f"Expected LOW, got {result['confidence_band']}"
    assert len(result["detected_data_classes"]) == 0, "Should not detect data classes in metadata"


# ============================================================================
# MUST BE HIGH (Real Sensitive Data)
# ============================================================================

def test_real_api_key():
    """Real API key should produce HIGH risk."""
    payload = {
        "user": "test@example.com",
        "api_key": "sk_live_ABC123XYZ789SECRETTOKEN1234567890"
    }
    
    result = extract_v2_json(payload)
    
    assert "credentials" in result["detected_data_classes"], "Should detect credentials"
    assert result["identifiers_present"] == True, "Should detect email"
    assert result["confidence_band"] in ("MEDIUM", "HIGH"), f"Expected MEDIUM/HIGH, got {result['confidence_band']}"


def test_real_email_and_medical_term():
    """Real email + medical term should produce HIGH risk."""
    payload = {
        "patient_email": "patient@hospital.com",
        "diagnosis": "Type 2 diabetes",
        "notes": "Patient diagnosed with hypertension"
    }
    
    result = extract_v2_json(payload)
    
    assert "medical" in result["detected_data_classes"], "Should detect medical data"
    assert result["identifiers_present"] == True, "Should detect email"
    assert result["confidence_band"] == "HIGH", f"Expected HIGH, got {result['confidence_band']}"


def test_credentials_in_prod_response():
    """Credentials in production response should produce HIGH risk."""
    payload = {
        "status": "success",
        "data": {
            "user_id": "12345",
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        }
    }
    
    result = extract_v2_json(payload)
    
    assert "credentials" in result["detected_data_classes"], "Should detect JWT token"
    assert result["confidence_band"] in ("MEDIUM", "HIGH"), f"Expected MEDIUM/HIGH, got {result['confidence_band']}"


def test_aws_access_key():
    """AWS access key should be detected."""
    payload = {
        "aws_credentials": {
            "access_key": "AKIAIOSFODNN7EXAMPLE",
            "region": "us-east-1"
        }
    }
    
    result = extract_v2_json(payload)
    
    assert "credentials" in result["detected_data_classes"], "Should detect AWS access key"


def test_google_api_key():
    """Google API key should be detected."""
    payload = {
        "api_config": {
            "google_api_key": "AIzaSyDaGmWKa4JsXZ-H_oGwNX8_Tj2h_1234567890"
        }
    }
    
    result = extract_v2_json(payload)
    
    assert "credentials" in result["detected_data_classes"], "Should detect Google API key"


# ============================================================================
# EDGE CASES
# ============================================================================

def test_empty_payload():
    """Empty payload should produce LOW risk."""
    result = extract_v2_json({})
    
    assert result["confidence_band"] == "LOW"
    assert len(result["detected_data_classes"]) == 0


def test_nested_empty_structures():
    """Nested empty structures should produce LOW risk."""
    payload = {
        "config": {
            "nodes": [],
            "edges": []
        }
    }
    
    result = extract_v2_json(payload)
    
    assert result["confidence_band"] == "LOW"
    assert len(result["detected_data_classes"]) == 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

