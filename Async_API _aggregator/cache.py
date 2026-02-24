# cache.py
from cachetools import TTLCache

# Initialize cache with 5-minute TTL
cache = TTLCache(maxsize=100, ttl=300)