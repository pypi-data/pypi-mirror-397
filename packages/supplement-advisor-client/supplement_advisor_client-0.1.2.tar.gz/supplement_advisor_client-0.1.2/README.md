# Supplement Advisor API Client

A simple Python client library for the Supplement Advisor API that helps you analyze supplement suitability for user profiles.

## Installation

```bash
pip install supplement-advisor-client
```

## Quick Start

```python
from supplement_advisor_client import analyze_supplement

api_key = "your-api-key"
ingredient_id = "coq10"
user_profile = {
    "age_range": "25-34",
    "sex": "female",
    "diet_type": "vegetarian",
    "goals": ["energy", "heart_health"],
    "conditions": [],
    "medications": [],
    "pregnancy_status": "none"
}

result = analyze_supplement(api_key, ingredient_id, user_profile)
print(f"Score: {result['overall_score']}")
print(f"Label: {result['suitability_label']}")
print(f"Risk Level: {result['risk_level']}")
```

## API Reference

### `analyze_supplement(api_key, ingredient_id, user_profile)`

Analyze supplement suitability for a user profile.

**Parameters:**
- `api_key` (str): API key for authentication (X-API-Key header)
- `ingredient_id` (str): ID of the supplement ingredient (e.g., 'coq10')
- `user_profile` (dict): Dictionary containing user profile information:
  - `age_range` (str): Age range (e.g., '25-34')
  - `sex` (str): Sex (e.g., 'female', 'male')
  - `diet_type` (str): Diet type (e.g., 'omnivore', 'vegetarian', 'vegan')
  - `goals` (List[str]): List of health goals (e.g., ['energy', 'heart_health'])
  - `conditions` (List[str], optional): List of medical conditions (default: [])
  - `medications` (List[str], optional): List of current medications (default: [])
  - `pregnancy_status` (str): Pregnancy status (e.g., 'none', 'pregnant', 'breastfeeding')

**Returns:**
- `dict`: Supplement analysis result containing:
  - `overall_score` (float): Suitability score from 0.0 to 1.0
  - `suitability_label` (str): Text label describing suitability
  - `evidence_level` (str): Evidence level (e.g., 'A', 'B', 'C')
  - `risk_level` (str): Risk level (e.g., 'low', 'medium', 'high', 'higher')
  - `key_benefits` (str): Key benefits description

**Raises:**
- `AuthenticationError`: If API key is invalid (401/403)
- `RateLimitError`: If rate limit is exceeded (429)
- `ServerError`: If server error occurs (5xx)
- `APIError`: If other API request fails

### `health_check`

Check API health status (no authentication required).

**Returns:**
- `dict`: Health status containing:
  - `status` (str): Status (e.g., 'healthy')
  - `service` (str): Service name (e.g., 'Supplement Advisor API')

**Raises:**
- `APIError`: If API request fails

## Error Handling

The client provides specific exception types for different error scenarios:

```python
from supplement_advisor_client import (
    analyze_supplement,
    AuthenticationError,
    RateLimitError,
    ServerError,
    APIError,
)

try:
    result = analyze_supplement(api_key, ingredient_id, user_profile)
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
except ServerError as e:
    print(f"Server error: {e}")
except APIError as e:
    print(f"API error: {e}")
```

## Examples

### Using with Production API

```python
from supplement_advisor_client import analyze_supplement

result = analyze_supplement(
    api_key="your-api-key",
    ingredient_id="coq10",
    user_profile={
        "age_range": "45-54",
        "sex": "male",
        "diet_type": "omnivore",
        "goals": ["heart_health"],
        "conditions": ["hypertension"],
        "medications": ["lisinopril"],
        "pregnancy_status": "none"
    }
)
```

### Checking API Health

```python
from supplement_advisor_client import health_check

status = health_check()
print(f"API Status: {status['status']}")
```

## Requirements

- Python 3.8+
- requests >= 2.31.0

## License

MIT License
