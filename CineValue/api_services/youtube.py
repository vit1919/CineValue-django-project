import asyncio
import logging
from typing import Optional
from ytmusicapi import YTMusic

logger = logging.getLogger(__name__)

ytmusic = YTMusic()


def get_soundtrack_url(movie_name: str) -> Optional[str]:
    search_query = f"{movie_name} movie soundtrack"

    try:
        results = ytmusic.search(search_query, filter='playlists', limit=1)
    except Exception as e:
        logger.error("[YT] Error querying YouTube Music: %s", e)
        return None

    if not results:
        logger.info("[YT] Soundtrack for '%s' not found", movie_name)
        return None

    playlist = results[0]
    browse_id = playlist.get('browseId')

    if not browse_id:
        return None

    playlist_id = browse_id[2:] if browse_id.startswith('VL') else browse_id
    youtube_url = f"https://www.youtube.com/playlist?list={playlist_id}"

    logger.info("[YT] Found playlist for '%s': %s", movie_name, youtube_url)
    return youtube_url


async def get_soundtrack_url_async(movie_name):
    return await asyncio.to_thread(get_soundtrack_url, movie_name)
