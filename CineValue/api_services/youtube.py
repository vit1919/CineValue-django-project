from typing import Optional
from ytmusicapi import YTMusic


ytmusic = YTMusic()

def get_soundtrack_url(movie_name: str) -> Optional[str]:
    search_query = f"{movie_name} movie soundtrack"
    
    try:
        results = ytmusic.search(search_query, filter='playlists', limit=1)
    except Exception as e:
        print(f"[YT] Ошибка при запросе к YouTube Music: {e}")
        return None

    if not results:
        print(f"[YT] Саундтрек для '{movie_name}' не найден")
        return None

    playlist = results[0]
    browse_id = playlist.get('browseId')
    
    if not browse_id:
        return None

    playlist_id = browse_id[2:] if browse_id.startswith('VL') else browse_id
    youtube_url = f"https://www.youtube.com/playlist?list={playlist_id}"
    
    print(f"[YT] Найден плейлист для '{movie_name}': {youtube_url}")
    return youtube_url