import logging
from functools import wraps
from typing import Callable, Any
import inspect
from django.core.cache import cache

logger = logging.getLogger(__name__)


def cache_api_response(key_prefix: str, timeout: int = 86400):
    def decorator(func: Callable) -> Callable:
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(tmdb_id: int, *args, **kwargs) -> dict[str, Any]:
                cache_key = f"{key_prefix}_{tmdb_id}"
                cached_data = cache.get(cache_key)

                if cached_data is not None:
                    logger.debug("[CACHE HIT] %s for TMDB ID: %s", key_prefix, tmdb_id)
                    return cached_data

                logger.info("[API REQUEST] %s for TMDB ID: %s", key_prefix, tmdb_id)
                data = await func(tmdb_id, *args, **kwargs)

                if data and isinstance(data, dict) and 'error' not in data:
                    logger.debug("[CACHE SET] %s for TMDB ID: %s", key_prefix, tmdb_id)
                    cache.set(cache_key, data, timeout)

                return data

            return async_wrapper

        @wraps(func)
        def wrapper(tmdb_id: int, *args, **kwargs) -> dict[str, Any]:
            cache_key = f"{key_prefix}_{tmdb_id}"
            cached_data = cache.get(cache_key)

            if cached_data is not None:
                logger.debug("[CACHE HIT] %s for TMDB ID: %s", key_prefix, tmdb_id)
                return cached_data

            logger.info("[API REQUEST] %s for TMDB ID: %s", key_prefix, tmdb_id)
            data = func(tmdb_id, *args, **kwargs)

            if data and isinstance(data, dict) and 'error' not in data:
                logger.debug("[CACHE SET] %s for TMDB ID: %s", key_prefix, tmdb_id)
                cache.set(cache_key, data, timeout)

            return data

        return wrapper

    return decorator
