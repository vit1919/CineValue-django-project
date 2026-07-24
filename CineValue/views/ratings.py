from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit
from ..models import Movie, Rating
from ..utils.validators import validate_rating


@ratelimit(key='ip', rate='30/m', block=True)
@login_required
@require_POST
def rate_movie(request, id):
    movie = get_object_or_404(Movie, id=id)

    try:
        rating = validate_rating(request.POST.get('rating'))
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    rating_obj, created = Rating.objects.update_or_create(
        user=request.user,
        movie=movie,
        defaults={'rating': rating, 'image_url': request.POST.get('image') or None},
    )

    return JsonResponse({
        'success': True,
        'rating': rating,
        'message': 'Rating saved!' if created else 'Rating updated!',
    })


@ratelimit(key='ip', rate='60/m', block=True)
@login_required
def users_ratings(request):
    rated_movies = (
        Rating.objects
        .filter(user=request.user)
        .select_related('movie')
        .order_by('-rated_at')
    )
    return render(request, 'users_ratings.html', {'users_ratings': rated_movies})


@ratelimit(key='ip', rate='60/m', block=True)
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
