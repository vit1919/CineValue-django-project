from django.core.cache import cache
from django.http import HttpResponse
from functools import wraps
from asgiref.sync import sync_to_async 

def async_ratelimit(limit=10, period=60):
    def decorator(func):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            ip = request.META.get('REMOTE_ADDR')
            key = f"ratelimit:{ip}"
            
         
            get_cache = sync_to_async(cache.get)
            set_cache = sync_to_async(cache.set)

            count = await get_cache(key, 0) 
            
            if count >= limit:
                return HttpResponse("Too Many Requests", status=429)
            
            await set_cache(key, count + 1, period) 
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
