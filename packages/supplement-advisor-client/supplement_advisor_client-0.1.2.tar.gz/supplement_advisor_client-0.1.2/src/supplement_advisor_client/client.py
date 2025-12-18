"""Client functions for Supplement Advisor API."""

import requests
from typing import Dict, List, Optional

from .errors import APIError, AuthenticationError, RateLimitError, ServerError


def analyze_supplement(
    api_key: str,
    ingredient_id: str,
    user_profile: Dict
) -> Dict:
    """
    Analyze supplement suitability for a user profile.
    
    Args:
        api_key: API key for authentication (X-API-Key header)
        ingredient_id: ID of the supplement ingredient (e.g., 'coq10')
        user_profile: Dictionary containing user profile information:
            - age_range: str (e.g., '25-34')
            - sex: str (e.g., 'female', 'male')
            - diet_type: str (e.g., 'omnivore', 'vegetarian', 'vegan')
            - goals: List[str] (e.g., ['energy', 'heart_health'])
            - conditions: List[str] (optional, default: [])
            - medications: List[str] (optional, default: [])
            - pregnancy_status: str (e.g., 'none', 'pregnant', 'breastfeeding')
    
    Returns:
        dict: Supplement analysis result containing:
            - overall_score: float (0.0 to 1.0)
            - suitability_label: str
            - evidence_level: str
            - risk_level: str
            - key_benefits: str
    
    Raises:
        AuthenticationError: If API key is invalid (401/403)
        RateLimitError: If rate limit is exceeded (429)
        ServerError: If server error occurs (5xx)
        APIError: If other API request fails
    """
    base_url ="https://supplements-advisor.martianspace.uk"
    url = f"{base_url}/api/v1/supplement/analyze"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key,
    }
    body = {
        "ingredient_id": ingredient_id,
        "user_profile": user_profile,
    }
    
    try:
        response = requests.post(url, json=body, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            _handle_error_response(response)
            
    except requests.exceptions.RequestException as e:
        raise APIError(
            status_code=0,
            error_type="RequestException",
            error_message=str(e)
        )


def health_check() -> Dict:
    """
    Check API health status (no authentication required).
    
    Returns:
        dict: Health status containing:
            - status: str (e.g., 'healthy')
            - service: str (e.g., 'Supplement Advisor API')
    
    Raises:
        APIError: If API request fails
    """
    base_url ="https://supplements-advisor.martianspace.uk"
    url = f"{base_url}/health"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            _handle_error_response(response)
            
    except requests.exceptions.RequestException as e:
        raise APIError(
            status_code=0,
            error_type="RequestException",
            error_message=str(e)
        )


def _handle_error_response(response: requests.Response) -> None:
    """Handle error responses and raise appropriate exceptions."""
    status_code = response.status_code
    
    # Try to parse error response
    error_type = None
    error_message = None
    
    try:
        error_data = response.json()
        if isinstance(error_data, dict):
            error = error_data.get("error") or error_data.get("detail")
            if isinstance(error, dict):
                error_type = error.get("type")
                error_message = error.get("message") or error.get("detail")
            elif isinstance(error, str):
                error_message = error
    except Exception:
        error_message = response.text or f"HTTP {status_code} error"
    
    # Raise appropriate exception based on status code
    if status_code in (401, 403):
        raise AuthenticationError(status_code, error_type, error_message)
    elif status_code == 429:
        raise RateLimitError(status_code, error_type, error_message)
    elif 500 <= status_code < 600:
        raise ServerError(status_code, error_type, error_message)
    else:
        raise APIError(status_code, error_type, error_message)

