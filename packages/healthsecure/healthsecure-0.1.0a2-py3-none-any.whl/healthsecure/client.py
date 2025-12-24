import requests
from typing import Optional

from .types import SignalPayload, SignalResponse
from .exceptions import (
    HealthSecureError,
    AuthenticationError,
    RateLimitError,
    APIError
)


class HealthSecureClient:
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        if not api_key:
            raise ValueError("api_key is required")

        self.api_key = api_key
        self.base_url = base_url or "https://api.yourdomain.com"

    def analyze_signal(self, payload: SignalPayload) -> SignalResponse:
        url = f"{self.base_url}/v1/analyze/signal"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload.model_dump(mode='json')
        )

        if response.status_code == 401:
            raise AuthenticationError("Invalid or missing API key")

        if response.status_code == 429:
            raise RateLimitError("Signal quota exceeded")

        if not response.ok:
            raise APIError(
                f"Request failed ({response.status_code}): {response.text}"
            )

        return SignalResponse(**response.json())

