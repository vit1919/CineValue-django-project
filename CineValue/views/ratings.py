from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from ..models import Movie, Rating


@login_required
@require_POST
def rate_movie(request, id):
    movie = get_object_or_404(Movie, id=id)
    rating_str = request.POST.get('rating')

    if not rating_str:
        return JsonResponse({'error': 'Rating is required'}, status=400)

    try:
        rating = int(rating_str)
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Rating must be a number'}, status=400)

    if not 1 <= rating <= 10:
        return JsonResponse({'error': 'Rating must be between 1 and 10'}, status=400)

    poster_url = request.POST.get('image') or None

    rating_obj, created = Rating.objects.update_or_create(
        user=request.user,
        movie=movie,
        defaults={
            'rating': rating,
            'image_url': poster_url,
        },
    )

    return JsonResponse({
        'success': True,
        'rating': rating,
        'message': 'Rating saved!' if created else 'Rating updated!',
    })


@login_required
def users_ratings(request):
    rated_movies = (
        Rating.objects
        .filter(user=request.user)
        .select_related('movie')
        .order_by('-rated_at')
    )
    return render(request, 'users_ratings.html', {'users_ratings': rated_movies})


@login_required
@require_POST
def remove_rating(request, id):
    movie = get_object_or_404(Movie, id=id)
    deleted, _ = Rating.objects.filter(user=request.user, movie=movie).delete()

    if deleted:
        messages.success(request, 'Rating removed.')
    else:
        messages.info(request, 'You have not rated this movie.')


    return redirect('users_ratings')