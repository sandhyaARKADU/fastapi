# routers/aggregate.py
import asyncio
import time
from fastapi import APIRouter, Response
from clients import weather_client, news_client
from cache import cache

router = APIRouter(prefix="/aggregate", tags=["aggregation"])

async def fetch_weather(city: str) -> dict:
    # Note: Requires a real API key in production
    data = await weather_client.get("/weather", {"q": city, "appid": "KEY"})
    if "error" in data:
        # Simulated fallback for demonstration
        await asyncio.sleep(0.5) 
        return {
            "source": "weather",
            "status": "simulated",
            "data": {"temp": 22.5, "description": "sunny", "city": city}
        }
    return {
        "source": "weather",
        "status": "ok",
        "data": {
            "temp": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "city": city
        }
    }

async def fetch_news(city: str) -> dict:
    # Simulated news fetch for demonstration
    await asyncio.sleep(0.8)
    return {
        "source": "news",
        "status": "ok",
        "data": [
            {"title": f"Local news for {city}", "url": "http://example.com/1"},
            {"title": f"Another update from {city}", "url": "http://example.com/2"}
        ]
    }

@router.get("/{city}")
async def aggregate(city: str, response: Response, no_cache: bool = False):
    cache_key = f"aggregate:{city.lower()}"
    
    if not no_cache and cache_key in cache:
        response.headers["X-Cache"] = "HIT"
        return cache[cache_key]
    
    response.headers["X-Cache"] = "MISS"
    
    start = time.perf_counter()
    
    # Concurrent execution using asyncio.gather
    results = await asyncio.gather(
        fetch_weather(city),
        fetch_news(city),
        return_exceptions=True
    )
    
    elapsed = time.perf_counter() - start
    
    data = {
        "city": city,
        "results": results,
        "timing_ms": round(elapsed * 1000, 2),
        "sources_ok": sum(1 for r in results if isinstance(r, dict) and r.get("status") in ["ok", "simulated"])
    }
    
    cache[cache_key] = data
    return data

@router.delete("/cache")
async def clear_cache():
    cache.clear()
    return {"message": "Cache cleared"}
