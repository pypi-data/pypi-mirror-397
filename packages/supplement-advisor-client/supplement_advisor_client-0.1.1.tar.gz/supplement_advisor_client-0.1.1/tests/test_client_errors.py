"""Tests for API client error handling."""

import pytest
from unittest.mock import Mock, patch
from supplement_advisor_client import (
    analyze_supplement,
    health_check,
    AuthenticationError,
    RateLimitError,
    ServerError,
    APIError,
)


def test_authentication_error():
    """Test authentication error (401)."""
    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.json.return_value = {"detail": "Invalid API key"}
    mock_response.text = '{"detail": "Invalid API key"}'
    
    with patch('supplement_advisor_client.client.requests.post', return_value=mock_response):
        with pytest.raises(AuthenticationError) as exc_info:
            analyze_supplement(
                api_key="invalid-key",
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
        
        assert exc_info.value.status_code == 401


def test_rate_limit_error():
    """Test rate limit error (429)."""
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.json.return_value = {"detail": "Rate limit exceeded"}
    mock_response.text = '{"detail": "Rate limit exceeded"}'
    
    with patch('supplement_advisor_client.client.requests.post', return_value=mock_response):
        with pytest.raises(RateLimitError) as exc_info:
            analyze_supplement(
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
        
        assert exc_info.value.status_code == 429


def test_server_error():
    """Test server error (500)."""
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.json.return_value = {"detail": "Internal server error"}
    mock_response.text = '{"detail": "Internal server error"}'
    
    with patch('supplement_advisor_client.client.requests.post', return_value=mock_response):
        with pytest.raises(ServerError) as exc_info:
            analyze_supplement(
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
        
        assert exc_info.value.status_code == 500


def test_request_exception():
    """Test request exception handling."""
    import requests
    with patch('supplement_advisor_client.client.requests.post', side_effect=requests.exceptions.ConnectionError("Connection error")):
        with pytest.raises(APIError) as exc_info:
            analyze_supplement(
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
        
        assert exc_info.value.status_code == 0
        assert "RequestException" in str(exc_info.value)

