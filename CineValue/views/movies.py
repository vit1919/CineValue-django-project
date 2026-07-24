from asgiref.sync import sync_to_async
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from CineValue.utils.async_rate_limit import async_ratelimit
from ..services.movie_service import MovieDetailService
from ..models import IMDb250, Movie
from django_ratelimit.decorators import ratelimit
from django.shortcuts import redirect


@ratelimit(key='ip', rate='20/m', block=True)
def index(request):

    top_movies = (Movie.objects.filter(vote_count__gte=1000).order_by('-vote_average')[:40])
    return render(request, 'index.html', {'top_movies': top_movies})



@ratelimit(key='ip', rate='100/m', block=True)
def search(request):
    query = request.GET.get('q', '').strip()
    if not query or len(query) < 2:
        return JsonResponse([], safe=False)

    movies_qs = (
        Movie.objects.filter(title__istartswith=query)
        .order_by('-popularity', 'title')[:10]
    )

    movies = list(movies_qs.values('id', 'title', 'year'))
    return JsonResponse(movies, safe=False)



    # vector = SearchVector('title', config='english')
    # search_query = SearchQuery(query, config='english')

    # movies_qs = Movie.objects.annotate(
    #                 rank=SearchRank(vector, search_query) 
    #             ).filter(
    #                 rank__gte=0.1
    #             ).order_by('-rank')[:10]



@async_ratelimit(limit=20, period=60)
async def search_result(request, id):
    movie = await sync_to_async(get_object_or_404)(Movie, id=id)

    user = await sync_to_async(lambda: request.user)()
    context = await MovieDetailService(movie, user).execute()
    context['rating_range'] = range(1, 11)

    return await sync_to_async(render)(request, 'result.html', context)


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

    movie_title = request.GET.get('q')
    if movie_title is not None:
        movie = Movie.objects.filter(title=movie_title).first()
        if movie:
            return redirect('search_result', id=movie.id)


    top250 = IMDb250.objects.all().order_by('rank')
    return render(request, 'imdb250.html', {'top250': top250})


@ratelimit(key='ip', rate='30/m', block=True)
def top250_tmdb(request):

    top250 = (
        Movie.objects.filter(vote_count__gte=1000)
        .order_by('-vote_average')[:250]
    )

    return render(request, 'top250_tmdb.html', {'top250': top250})
