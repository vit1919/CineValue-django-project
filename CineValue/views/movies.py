from django.db.models import Q
from django.http import HttpResponseServerError, JsonResponse
from django.shortcuts import get_object_or_404, render

from ..models import IMDb250, Liked, Movie, Rating, WatchList
from ..api_services import get_kinopoisk_data, get_whatson_data, get_soundtrack_url


def index(request):

    top_movies = (
        Movie.objects.filter(vote_count__gte=1000)
        .order_by('-vote_average')[:40]
    )

    return render(request, 'index.html', {'top_movies': top_movies})


def search(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse([], safe=False)

    movies_qs = (
        Movie.objects.filter(title__icontains=query)
        .order_by('-popularity', 'title')[:10]
    )
    movies = list(movies_qs.values('id', 'title', 'year'))
    return JsonResponse(movies, safe=False)


def search_result(request, id):
    movie = get_object_or_404(Movie, id=id)
    tmdb_id = movie.tmdb_id

    data_whatson = get_whatson_data(tmdb_id)
    if isinstance(data_whatson, dict) and 'error' in data_whatson:
        data_whatson = None

    budget_m = round(movie.budget / 1_000_000) if movie.budget else 0
    revenue_m = round(movie.revenue / 1_000_000) if movie.revenue else 0

    kp = get_kinopoisk_data(tmdb_id)
    if isinstance(kp, dict) and 'error' in kp:
        kp = None

    service_count=0
    rating_count=0

    if data_whatson:

        kp_rating = kp.get('rating', {}).get('kp', '–')
        if kp_rating != '–' and kp_rating != 0:
            service_count += 1
            rating_count += kp_rating
        
        
        imdb_rating = (data_whatson.get('imdb') or {}).get('users_rating', '–')
        if imdb_rating != '–':
            service_count += 1
            rating_count += imdb_rating

        rt_rating_critics = (data_whatson.get('rotten_tomatoes') or {}).get('critics_rating', '–')
        if rt_rating_critics != '–':
            service_count += 1
            rating_count += rt_rating_critics / 10

        metacritic_rating = (data_whatson.get('metacritic') or {}).get('critics_rating', '–')
        if metacritic_rating != '–':
            service_count += 1
            rating_count += metacritic_rating / 10

        letterboxd_rating = (data_whatson.get('letterboxd') or {}).get('users_rating', '–')
        if letterboxd_rating != '–':
            service_count += 1
            rating_count += letterboxd_rating * 2

        average_rating = round(rating_count / service_count, 1) if service_count > 0 else '–'
    else:
        average_rating = None

    if request.user.is_authenticated:
        is_in_watchlist = (
            request.user.is_authenticated and 
            WatchList.objects.filter(user=request.user, movie=movie).exists()
        )
        is_in_liked = (
            request.user.is_authenticated and 
            Liked.objects.filter(user=request.user, movie=movie).exists()
        )
        is_rated = (
            request.user.is_authenticated and 
            Rating.objects.filter(user=request.user, movie=movie).exists()
        )
    else:
        is_in_watchlist = False
        is_in_liked = False
        is_rated = False

    soundtrack_url = get_soundtrack_url(movie.title)

    # Backdrop URL: prefer movie.backdrop_path, fallback to poster from whatson
    if movie.backdrop_path:
        backdrop_url = f'https://image.tmdb.org/t/p/original{movie.backdrop_path}'
    elif data_whatson and data_whatson.get('image'):
        backdrop_url = data_whatson.get('image')
    else:
        backdrop_url = ''

    # Parse genres from movie model as fallback
    movie_genres = []
    if movie.genres:
        movie_genres = [g.strip() for g in movie.genres.split(',') if g.strip()]

    context = {
        'movie': movie,
        'data_whatson': data_whatson,
        'kp': kp,
        'budget_m': budget_m,
        'revenue_m': revenue_m,
        'is_in_watchlist': is_in_watchlist,
        'is_in_liked': is_in_liked,
        'is_rated': is_rated,
        'soundtrack_url': soundtrack_url,
        'rating_range': range(1, 11),
        'average_rating': average_rating,
        'movie_genres': movie_genres,
        'backdrop_url': backdrop_url,
    }
    return render(request, 'result.html', context)



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

  
def top250_imdb(request):
    top250 = IMDb250.objects.all().order_by('rank')
    return render(request, 'imdb250.html', {'top250': top250})



def top250_tmdb(request):
    top250 = (
        Movie.objects.filter(vote_count__gte=1000)
        .order_by('-vote_average')[:250]
    )
    return render(request, 'top250_tmdb.html', {'top250': top250})

