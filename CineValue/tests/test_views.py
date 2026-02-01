from django.urls import reverse
import pytest

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









