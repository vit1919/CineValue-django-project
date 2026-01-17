from django.db.models import Q
from django.http import HttpResponseServerError, JsonResponse
from django.shortcuts import get_object_or_404, render
from ..utils.movie_utils import count_avg_rating, check_user_movie_status, get_backdrop_url 
from ..models import IMDb250, Liked, Movie, Rating, WatchList
from ..api_services import get_kinopoisk_data, get_whatson_data, get_soundtrack_url


def index(request):

    top_movies = (Movie.objects.filter(vote_count__gte=1000).order_by('-vote_average')[:40])
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

    kp = get_kinopoisk_data(tmdb_id)
    if isinstance(kp, dict) and 'error' in kp:
        kp = None

    average_rating = count_avg_rating(kp, data_whatson)
    user_status = check_user_movie_status(request.user, movie)
    soundtrack_url = get_soundtrack_url(movie.title)
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

