import requests
from django.core.cache import cache
from movie import settings

def get_kp_api(request, tmdb_id): 

    cache_key = f"kp_data_{tmdb_id}"
    cached_data = cache.get(cache_key)

    if cached_data:
        print(f"Данные для TMDB ID {tmdb_id} взяты из кеша!")
        return cached_data

    print('сделаем запросик api')

    api_key = settings.KINOPOISK_API_KEY
    if not api_key:
        return {'error': 'KINOPOISK_API_KEY не настроен в окружении/настройках.'}
    
    url = f"https://api.kinopoisk.dev/v1.4/movie?page=1&limit=1&selectFields=rating&selectFields=votes&externalId.tmdb={tmdb_id}"
    headers = {"X-API-KEY": api_key, "Accept": "application/json"}


    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()


        docs = data.get("docs") or []
        if docs:
            doc = docs[0]
        else:
            doc = None

        cache.set(cache_key, doc, timeout=86400)

        return doc
 
    except requests.RequestException as e:
        return {'error': f'Ошибка запроса к kinopoisk.dev: {e}'}

    
def get_whatson_api(request, tmdb_id):

    cache_key = f"whatson_data_{tmdb_id}"
    cached_data = cache.get(cache_key)

    if cached_data:
        print(f"Данные для TMDB ID {tmdb_id} взяты из кеша!")
        return cached_data

    api_url = f"https://whatson-api.onrender.com/movie/{tmdb_id}?ratings_filters=imdb_users,rottentomatoes_users&append_to_response=critics_rating_details"

    try:
        response = requests.get(api_url)
        response.raise_for_status()

        data = response.json()
        cache.set(cache_key, data, timeout=86400)
        
        return data

    
    except requests.RequestException as e:
        return {'error': f"API request failed: {str(e)}"}
    
    except ValueError as e: 
        return {'error': f"Invalid API response: {str(e)}"}