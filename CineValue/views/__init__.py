from .auth import signup
from .liked import *
from .movies import index, search, search_result, top250_tmdb, search_result_real
from .ratings import rate_movie, remove_rating, users_ratings
from .watchlist import (
    remove_watchlist_movie,
    remove_watchlist_movie_inresult,
    to_watchlist,
    watchlist,
)

