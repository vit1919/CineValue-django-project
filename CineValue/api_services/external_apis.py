from wsgiref import headers
import requests
from django.conf import settings
import httpx
from .cache_utils import cache_api_response


@cache_api_response(key_prefix="kp_data", timeout=86400)
async def get_kinopoisk_data_async(tmdb_id: int) -> dict:
    api_key = settings.KINOPOISK_API_KEY
    if not api_key:
        return {'error': 'KINOPOISK_API_KEY не настроен в settings'}

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
            print(f"[KP] Фильм с TMDB ID {tmdb_id} не найден")
            return {'error': 'Фильм не найден в Kinopoisk'}

        return docs[0]
 
    except httpx.TimeoutException:
        return {'error': 'Превышено время ожидания ответа от Kinopoisk API'}
    except httpx.RequestError as e:
        return {'error': f'Ошибка запроса к Kinopoisk API: {str(e)}'}


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

    except httpx.TimeoutException:
        return {'error': 'Превышено время ожидания ответа от WhatsOn API'}
    except httpx.RequestError as e:
        return {'error': f'Ошибка запроса к WhatsOn API: {str(e)}'}
    except ValueError as e:
        return {'error': f'Некорректный ответ от WhatsOn API: {str(e)}'}