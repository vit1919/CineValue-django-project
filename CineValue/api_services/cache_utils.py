from functools import wraps
from typing import Callable, Any
import inspect
from django.core.cache import cache


def cache_api_response(key_prefix: str, timeout: int = 86400):
    def decorator(func: Callable) -> Callable:
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(tmdb_id: int, *args, **kwargs) -> dict[str, Any]:
                cache_key = f"{key_prefix}_{tmdb_id}"
                cached_data = cache.get(cache_key)

                if cached_data is not None:
                    print(f"[CACHE HIT] {key_prefix} для TMDB ID: {tmdb_id}")
                    return cached_data

                print(f"[API REQUEST] {key_prefix} для TMDB ID: {tmdb_id}")
                data = await func(tmdb_id, *args, **kwargs)

                if data and isinstance(data, dict) and 'error' not in data:
                    print(f"[CACHE SET] {key_prefix} для TMDB ID: {tmdb_id}")
                    cache.set(cache_key, data, timeout)

                return data

            return async_wrapper

        @wraps(func)
        def wrapper(tmdb_id: int, *args, **kwargs) -> dict[str, Any]:
            cache_key = f"{key_prefix}_{tmdb_id}"
            cached_data = cache.get(cache_key)

            if cached_data is not None:
                print(f"[CACHE HIT (взяли их кэша)] {key_prefix} для TMDB ID: {tmdb_id}")
                return cached_data

            print(f"[API REQUEST] {key_prefix} для TMDB ID: {tmdb_id}")
            data = func(tmdb_id, *args, **kwargs)

            if data and isinstance(data, dict) and 'error' not in data:
                print(f"[CACHE SET (взяли их кэша)] {key_prefix} для TMDB ID: {tmdb_id}")
                cache.set(cache_key, data, timeout)

            return data

        return wrapper

    return decorator
