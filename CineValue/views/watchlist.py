from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit
from ..models import Movie, WatchList

@ratelimit(key='ip', rate='60/m', block=True)
@login_required
@require_POST
def to_watchlist(request, id):
    movie = get_object_or_404(Movie, id=id)
    poster_url = request.POST.get('image')
    watchlist_entry, created = WatchList.objects.get_or_create(
        user=request.user,
        movie=movie,
    )
    if created and poster_url:
        watchlist_entry.image_url = poster_url
        watchlist_entry.save()

    return redirect('search_result', id=movie.id)


@ratelimit(key='ip', rate='30/m', block=True)
@login_required
def watchlist(request):
    user_watchlist = (
        WatchList.objects.filter(user=request.user)
        .select_related('movie')
        .order_by('-added_at')
    )
    return render(request, 'watchlist.html', {'watchlist': user_watchlist})


@ratelimit(key='ip', rate='60/m', block=True)
@login_required
@require_POST
def remove_watchlist_movie(request, id):
    movie = get_object_or_404(Movie, id=id)
    WatchList.objects.filter(user=request.user, movie=movie).delete()
    return redirect('watchlist')


@ratelimit(key='ip', rate='30/m', block=True)
@login_required
@require_POST
def remove_watchlist_movie_inresult(request, id):
    movie = get_object_or_404(Movie, id=id)
    WatchList.objects.filter(user=request.user, movie=movie).delete()
    return redirect('search_result', id=movie.id)
