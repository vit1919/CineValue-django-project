import logging
import requests
from django.conf import settings
import httpx
from .cache_utils import cache_api_response

logger = logging.getLogger(__name__)

@cache_api_response(key_prefix="kp_data", timeout=86400)
async def get_kinopoisk_data_async(tmdb_id: int) -> dict:
    api_key = settings.KINOPOISK_API_KEY
    if not api_key:
        return {'error': 'KINOPOISK_API_KEY is not configured in settings'}

    url = (
        f"https://api.kinopoisk.dev/v1.4/movie"
        f"?page=1&limit=1"
        f"&selectFields=rating&selectFields=votes"
        f"&externalId.tmdb={tmdb_id}"
    )
    headers = {
        "X-API-KEY": api_key,
        "Accept": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

        docs = data.get("docs", [])
        if not docs:
            logger.warning("[KP] Movie with TMDB ID %s not found", tmdb_id)
            return {'error': 'Movie not found in Kinopoisk'}

        return docs[0]

    except httpx.TimeoutException:
        return {'error': 'Kinopoisk API timeout'}
    except httpx.RequestError as e:
        return {'error': f'Kinopoisk API request error: {str(e)}'}


@cache_api_response(key_prefix="whatson_data", timeout=86400)
async def get_whatson_data_async(tmdb_id: int) -> dict:
    url = (
        f"https://whatson-api.onrender.com/movie/{tmdb_id}"
        f"?ratings_filters=imdb_users,rottentomatoes_users"
        f"&append_to_response=critics_rating_details"
    )

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        return data

    except httpx.HTTPStatusError as e:
        return {'error': f'WhatsOn API status error: {e.response.status_code}'}
    except httpx.TimeoutException:
        return {'error': 'WhatsOn API timeout'}
    except httpx.RequestError as e:
        return {'error': f'WhatsOn API request error: {str(e)}'}
    except ValueError as e:
        return {'error': f'Invalid response from WhatsOn API: {str(e)}'}
