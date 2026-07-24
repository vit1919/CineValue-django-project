import asyncio
from asgiref.sync import sync_to_async
from ..api_services import get_kinopoisk_data_async, get_whatson_data_async, get_soundtrack_url_async
from ..utils.movie_utils import count_avg_rating, get_backdrop_url
from ..models import WatchList, Liked, Rating


class MovieDetailService:
    def __init__(self, movie, user):
        self.movie = movie
        self.user = user

    async def execute(self) -> dict:
        data_whatson, kp, soundtrack_url = await self._fetch_external_data()

        data_whatson = self._clean_api_response(data_whatson)
        kp = self._clean_api_response(kp)

        return {
            'movie': self.movie,
            'data_whatson': data_whatson,
            'kp': kp,
            'soundtrack_url': soundtrack_url,
            'average_rating': count_avg_rating(kp, data_whatson),
            'backdrop_url': get_backdrop_url(self.movie, data_whatson),
            'movie_genres': self._parse_genres(),
            **(await self._get_user_status()),
        }

    async def _fetch_external_data(self):
        return await asyncio.gather(
            get_whatson_data_async(self.movie.tmdb_id),
            get_kinopoisk_data_async(self.movie.tmdb_id),
            get_soundtrack_url_async(self.movie.title)
        )

    @staticmethod
    def _clean_api_response(response):
        return None if isinstance(response, dict) and 'error' in response else response

    def _parse_genres(self):
        if not self.movie.genres:
            return []
        return [g.strip() for g in self.movie.genres.split(',') if g.strip()]

    async def _get_user_status(self):
        if not self.user.is_authenticated:
            return {
                'is_in_watchlist': False,
                'is_in_liked': False,
                'is_rated': False,
            }
        return {
            'is_in_watchlist': await sync_to_async(WatchList.objects.filter(user=self.user, movie=self.movie).exists)(),
            'is_in_liked': await sync_to_async(Liked.objects.filter(user=self.user, movie=self.movie).exists)(),
            'is_rated': await sync_to_async(Rating.objects.filter(user=self.user, movie=self.movie).exists)(),
        }
