from django.urls import reverse
import pytest
from ..models import Movie, WatchList


@pytest.mark.django_db
def test_index_page_loads(client):
    
    url = reverse('index') 
    response = client.get(url)
    
    assert response.status_code == 200
    assert "CineValue" in response.content.decode()


@pytest.mark.django_db
def test_index_page_movies(client, top_rated_movies):
    url = reverse('index') 
    response = client.get(url)

    assert 'top_movies' in response.context
    assert len(response.context['top_movies']) >= 10



@pytest.mark.django_db
def test_search_functionality(client, movie):

    url = reverse('search')
    response = client.get(url, {'q': 'Myadel'})
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert 'Myadel' in data[0]['title']

    response = client.get(url, {'q': 'oppdjjwhkdjf'})
    data = response.json()
    assert len(data) == 0

    response = client.get(url, {'q': 'j'})
    data = response.json()
    assert len(data) == 0



@pytest.mark.django_db
def test_search_after_enter(client, movie, movies_list):

    url = reverse('search_result_real')
    response = client.get(url, {'movie_name': 'Myadel'})

    assert response.status_code == 200
    assert 'Myadel' in response.context['search_results'][0]['title']

@pytest.mark.django_db
def test_watchlist_requires_login(client):
    response = client.get(reverse('watchlist'))
    assert response.status_code in (302, 301)

@pytest.mark.django_db
def test_watchlist_authenticated(authenticated_client):
    response = authenticated_client.get(reverse('watchlist'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_add_to_watchlist(authenticated_client, movie):
    response = authenticated_client.post(
        reverse('to_watchlist', args=[movie.id]),
        {'image': 'https://example.com/poster.jpg'}
    )
    assert response.status_code in (302, 301)
    assert WatchList.objects.filter(movie=movie).exists()

@pytest.mark.django_db
def test_remove_from_watchlist(authenticated_client, watchlist_item):
    movie_id = watchlist_item.movie.id
    response = authenticated_client.post(reverse('remove_watchlist_movie', args=[movie_id]))
    assert response.status_code in (302, 301)
    assert not WatchList.objects.filter(id=watchlist_item.id).exists()




