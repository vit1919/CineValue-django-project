import asyncio
from asgiref.sync import sync_to_async
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from CineValue.utils.async_rate_limit import async_ratelimit
from ..api_services import get_kinopoisk_data_async, get_whatson_data_async, get_soundtrack_url_async
from ..utils.movie_utils import count_avg_rating, check_user_movie_status, get_backdrop_url
from ..models import IMDb250, Movie
from django_ratelimit.decorators import ratelimit
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank


@ratelimit(key='ip', rate='20/m', block=True)
def index(request):

    top_movies = (Movie.objects.filter(vote_count__gte=1000).order_by('-vote_average')[:40])
    return render(request, 'index.html', {'top_movies': top_movies})

@ratelimit(key='ip', rate='100/m', block=True)
def search(request):
    query = request.GET.get('q', '').strip()
    if not query or len(query) < 2:
        return JsonResponse([], safe=False)


    # vector = SearchVector('title', config='english')
    # search_query = SearchQuery(query, config='english')

    # movies_qs = Movie.objects.annotate(
    #                 rank=SearchRank(vector, search_query) 
    #             ).filter(
    #                 rank__gte=0.1
    #             ).order_by('-rank')[:10]

    movies_qs = (
        Movie.objects.filter(title__istartswith=query)
        .order_by('-popularity', 'title')[:10]
    )

    movies = list(movies_qs.values('id', 'title', 'year'))
    return JsonResponse(movies, safe=False)



@async_ratelimit(limit=20, period=60)
async def search_result(request, id):

    movie = await sync_to_async(get_object_or_404)(Movie, id=id)
    tmdb_id = movie.tmdb_id


    data_task = get_whatson_data_async(tmdb_id)
    kp_task = get_kinopoisk_data_async(tmdb_id)
    soundtrack_task = get_soundtrack_url_async(movie.title)

    data_whatson, kp, soundtrack_url = await asyncio.gather(
        data_task, kp_task, soundtrack_task
    )

    if isinstance(data_whatson, dict) and 'error' in data_whatson:
        data_whatson = None
    if isinstance(kp, dict) and 'error' in kp:
        kp = None

    average_rating = count_avg_rating(kp, data_whatson)
    user_status = await sync_to_async(check_user_movie_status)(request.user, movie)
    backdrop_url = get_backdrop_url(movie, data_whatson)

    movie_genres = []
    if movie.genres:
        movie_genres = [g.strip() for g in movie.genres.split(',') if g.strip()]

    context = {
        'movie': movie,
        'data_whatson': data_whatson,
        'kp': kp,
        **user_status,
        'soundtrack_url': soundtrack_url,
        'rating_range': range(1, 11),
        'average_rating': average_rating,
        'movie_genres': movie_genres,
        'backdrop_url': backdrop_url,
    }
    return render(request, 'result.html', context)


@ratelimit(key='ip', rate='20/m', block=True)
def search_result_real(request):

    movie = request.GET.get('movie_name', '').strip()
    if not movie:
        movies = []
        
    else:
        result = (
            Movie.objects.filter(title__icontains=movie)
            .order_by('-popularity', 'title')[:10]
        )
        movies = list(result.values('id', 'title', 'year'))

    return render(request, 'real_result.html', {'search_results': movies})


@ratelimit(key='ip', rate='30/m', block=True)
def top250_imdb(request):

    top250 = IMDb250.objects.all().order_by('rank')
    return render(request, 'imdb250.html', {'top250': top250})


@ratelimit(key='ip', rate='30/m', block=True)
def top250_tmdb(request):

    top250 = (
        Movie.objects.filter(vote_count__gte=1000)
        .order_by('-vote_average')[:250]
    )

    return render(request, 'top250_tmdb.html', {'top250': top250})

