from .auth import signup
from .liked import like, remove_liked_movie
from .movies import index, search, search_result, top250_tmdb
from .ratings import rate_movie, remove_rating, users_ratings
from .watchlist import (
    remove_watchlist_movie,
    remove_watchlist_movie_inresult,
    to_watchlist,
    watchlist,
)

__all__ = [
    'index',
    'search',
    'search_result',
    'top250_tmdb',
    'signup',
    'to_watchlist',
    'watchlist',
    'remove_watchlist_movie',
    'remove_watchlist_movie_inresult',
    'like',
    'remove_liked_movie',
    'rate_movie',
    'users_ratings',
    'remove_rating',
]
