"""Tests for successful API client operations."""

import pytest
from unittest.mock import Mock, patch
from supplement_advisor_client import analyze_supplement, health_check


def test_analyze_supplement_success():
    """Test successful supplement analysis."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "overall_score": 0.85,
        "suitability_label": "Highly Suitable",
        "evidence_level": "A",
        "risk_level": "low",
        "key_benefits": "Supports heart health and energy production"
    }
    
    with patch('supplement_advisor_client.client.requests.post', return_value=mock_response):
        result = analyze_supplement(
            api_key="test-key",
            ingredient_id="coq10",
            user_profile={
                "age_range": "25-34",
                "sex": "female",
                "diet_type": "vegetarian",
                "goals": ["energy"],
                "conditions": [],
                "medications": [],
                "pregnancy_status": "none"
            }
        )
        
        assert result["overall_score"] == 0.85
        assert result["suitability_label"] == "Highly Suitable"
        assert result["evidence_level"] == "A"
        assert result["risk_level"] == "low"


def test_health_check_success():
    """Test successful health check."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "healthy",
        "service": "Supplement Advisor API"
    }
    
    with patch('supplement_advisor_client.client.requests.get', return_value=mock_response):
        result = health_check()
        
        assert result["status"] == "healthy"
        assert result["service"] == "Supplement Advisor API"

