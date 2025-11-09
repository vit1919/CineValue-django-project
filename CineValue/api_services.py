import requests
from django.core.cache import cache
from movie import settings
from ytmusicapi import YTMusic
from functools import wraps

ytmusic = YTMusic()

def cache_api(key_prefix, timeout=86400):
    def decorator(func):
        @wraps(func)
        def wrapper(request, tmdb_id):
            cache_key = f"{key_prefix}_{tmdb_id}"
            cached_data = cache.get(cache_key)

            if cached_data is not None:
                print(f"Данные для {key_prefix} {tmdb_id} взяты из кеша")
                return cached_data
            
            print(f'api request for {key_prefix} {tmdb_id}')
            data = func(request, tmdb_id)

            if data and isinstance(data, dict) and not 'error' in data:
                print(f'caching data for {key_prefix} {tmdb_id}')
                cache.set(cache_key, data, timeout)

            return data
        return wrapper
    return decorator


@cache_api(key_prefix="kp_data", timeout=86400)
def get_kp_api(request, tmdb_id): 


    api_key = settings.KINOPOISK_API_KEY
    if not api_key:
        return {'error': 'KINOPOISK_API_KEY не настроен .'}
    
    url = f"https://api.kinopoisk.dev/v1.4/movie?page=1&limit=1&selectFields=rating&selectFields=votes&externalId.tmdb={tmdb_id}"
    headers = {"X-API-KEY": api_key, "Accept": "application/json"}


    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        docs = data.get("docs", [])

        if not docs:
            print('not found in kp') 
            return {'error': 'not found'}

        return docs[0]  
 
    except requests.RequestException as e:
        return {'error': f'Ошибка запроса к kinopoisk.dev: {e}'}

@cache_api(key_prefix="whatson_data", timeout=86400)
def get_whatson_api(request, tmdb_id):

    api_url = f"https://whatson-api.onrender.com/movie/{tmdb_id}?ratings_filters=imdb_users,rottentomatoes_users&append_to_response=critics_rating_details"

    try:
        response = requests.get(api_url)
        response.raise_for_status()

        data = response.json()
        
        return data

    
    except requests.RequestException as e:
        return {'error': f"API request failed: {str(e)}"}
    
    except ValueError as e: 
        return {'error': f"Invalid API response: {str(e)}"}
    

def soundtrack(request, movie_name):

    search_query = f"{movie_name} movie soundtrack"
    results = ytmusic.search(search_query, filter='playlists', limit=1)

    if not results:
        return None 

    playlist = results[0]
    browse_id = playlist['browseId']

    if browse_id.startswith('VL'):
        youtube_playlist_id = browse_id[2:]
    else:
        youtube_playlist_id = browse_id
    
    youtube_playlist_url = f"https://www.youtube.com/playlist?list={youtube_playlist_id}"
    # youtube_music_url = f"https://music.youtube.com/playlist?list={browse_id}"

    return youtube_playlist_url




    