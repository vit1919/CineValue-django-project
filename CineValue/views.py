from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseServerError
from django.core.cache import cache
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from .forms import SignUpForm

from movie import settings
from .models import Movie
from django.http import JsonResponse
import requests


def index(request):
    return render(request, 'index.html')


def search(request):
    q = request.GET.get('q', '').strip()
    if q:
        movies_qs = Movie.objects.filter(Q(title__icontains=q)).order_by('-popularity', 'title')[:10]
        movies = list(movies_qs.values('id', 'title', 'year'))
    else:
        movies = []
    return JsonResponse(movies, safe=False)



def search_result(request, id):
    movie = get_object_or_404(Movie, id=id)
    tmdb_id = movie.tmdb_id

    data_whatson = get_whatson_api(request, tmdb_id)

    if isinstance(data_whatson, dict) and 'error' in data_whatson:
        return HttpResponseServerError(data_whatson['error'])
    
    # movie.budget = movie.budget/1000000
    # movie.revenue = round(movie.revenue/1000000)

    budget_m = round(movie.budget/1000000)
    revenue_m = round(movie.revenue/1000000)

    kp = get_kp_api(request, tmdb_id)

    if isinstance(kp, dict) and 'error' in kp:
        return HttpResponseServerError(kp['error'])

    #kp = None
    
    to_template = {
            'movie':movie,
            'data_whatson':data_whatson,
            'kp':kp,
            'budget_m':budget_m,
            'revenue_m':revenue_m,
                   }

    return render(request, 'result.html', to_template)



def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            messages.success(request, 'Registered!')
            return redirect('/')
    else:
        form = SignUpForm()
    
    return render(request, 'signup.html', {'form': form})


def get_kp_api(request, tmdb_id): 

    cache_key = f"kp_data_{tmdb_id}"
    cached_data = cache.get(cache_key)

    if cached_data:
        print(f"Данные для TMDB ID {tmdb_id} взяты из кеша!")
        return cached_data

    print('сделаем запросик api')

    api_key = settings.KINOPOISK_API_KEY
    if not api_key:
        return {'error': 'KINOPOISK_API_KEY не настроен в окружении/настройках.'}
    
    url = f"https://api.kinopoisk.dev/v1.4/movie?page=1&limit=1&selectFields=rating&selectFields=votes&externalId.tmdb={tmdb_id}"
    headers = {"X-API-KEY": api_key, "Accept": "application/json"}


    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()


        docs = data.get("docs") or []
        if docs:
            doc = docs[0]
        else:
            doc = None

        cache.set(cache_key, doc, timeout=86400)

        return doc
 
    except requests.RequestException as e:
        return {'error': f'Ошибка запроса к kinopoisk.dev: {e}'}

    

    
def get_whatson_api(request, tmdb_id):

    api_url = f"https://whatson-api.onrender.com/movie/{tmdb_id}?ratings_filters=imdb_users,rottentomatoes_users&append_to_response=critics_rating_details"

    try:
        response = requests.get(api_url)
        response.raise_for_status()

        data = response.json()
        return data

    
    except requests.RequestException as e:
        return {'error': f"API request failed: {str(e)}"}
    
    except ValueError as e: 
        return {'error': f"Invalid API response: {str(e)}"}