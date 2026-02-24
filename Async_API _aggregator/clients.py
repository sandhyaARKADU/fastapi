# clients.py
import httpx
from typing import Dict, Any

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def get(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}{endpoint}", params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                return {"error": str(e), "status": e.response.status_code}
            except Exception as e:
                return {"error": str(e)}

weather_client = APIClient("https://api.openweathermap.org/data/2.5")
news_client = APIClient("https://newsapi.org/v2")