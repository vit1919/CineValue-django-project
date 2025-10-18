from django.db.models import Q
from django.http import HttpResponseServerError, JsonResponse
from django.shortcuts import get_object_or_404, render

from ..models import Liked, Movie, Rating, WatchList
from ..api_services import get_kp_api, get_whatson_api


def index(request):
    return render(request, 'index.html')


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

    data_whatson = get_whatson_api(request, tmdb_id)
    if isinstance(data_whatson, dict) and 'error' in data_whatson:
        return HttpResponseServerError(data_whatson['error'])

    budget_m = round(movie.budget / 1_000_000) if movie.budget else 0
    revenue_m = round(movie.revenue / 1_000_000) if movie.revenue else 0

    kp = get_kp_api(request, tmdb_id)
    if isinstance(kp, dict) and 'error' in kp:
        return HttpResponseServerError(kp['error'])

    if request.user.is_authenticated:
        is_in_watchlist = WatchList.objects.filter(
            user=request.user,
            movie=movie,
        ).exists()
        is_in_liked = Liked.objects.filter(
            user=request.user,
            movie=movie,
        ).exists()
        is_rated = Rating.objects.filter(
            user=request.user,
            movie=movie,
        ).exists()
    else:
        is_in_watchlist = False
        is_in_liked = False
        is_rated = False

    context = {
        'movie': movie,
        'data_whatson': data_whatson,
        'kp': kp,
        'budget_m': budget_m,
        'revenue_m': revenue_m,
        'is_in_watchlist': is_in_watchlist,
        'is_in_liked': is_in_liked,
        'is_rated': is_rated,
        'rating_range': range(1, 11),
    }
    return render(request, 'result.html', context)


def top250_tmdb(request):
    top250 = (
        Movie.objects.filter(vote_count__gte=1000)
        .order_by('-vote_average')[:250]
    )
    return render(request, 'top250_tmdb.html', {'top250': top250})
