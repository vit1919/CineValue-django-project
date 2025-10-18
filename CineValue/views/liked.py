from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from ..models import Liked, Movie


@login_required
@require_POST
def like(request, id):
    movie = get_object_or_404(Movie, id=id)
    poster_url = request.POST.get('image')
    liked_entry, created = Liked.objects.get_or_create(
        user=request.user,
        movie=movie,
    )
    if created and poster_url:
        liked_entry.image_url = poster_url
        liked_entry.save()

    return redirect('search_result', id=movie.id)


@login_required
@require_POST
def remove_liked_movie(request, id):
    movie = get_object_or_404(Movie, id=id)
    Liked.objects.filter(user=request.user, movie=movie).delete()
    return redirect('search_result', id=movie.id)
