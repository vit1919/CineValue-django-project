import pytest
from django.contrib.auth.models import User
from CineValue.models import Movie, WatchList, Liked, Rating, IMDb250

@pytest.fixture
def user(db):
    
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def authenticated_client(client, user):
    
    client.login(username='testuser', password='testpass123')
    return client

@pytest.fixture
def movie(db):
    return Movie.objects.create(
        title='Myadel',
        original_title='Myadel',
        original_language='en',
        year=1967,
        overview='i do not know what to type in here',
        tmdb_id=1241000
        
    )

@pytest.fixture
def watchlist_item(db, user, movie):
    
    return WatchList.objects.create(
        user=user,
        movie=movie,
        image_url='https://example.com/poster.jpg'
    )

@pytest.fixture
def liked_item(db, user, movie):
  
    return Liked.objects.create(
        user=user,
        movie=movie,
        image_url='https://example.com/poster.jpg'
    )

@pytest.fixture
def rating_item(db, user, movie):
    
    return Rating.objects.create(
        user=user,
        movie=movie,
        rating=9,
        image_url='https://example.com/poster.jpg'
    )


@pytest.fixture
def top_rated_movies(db):
    
    movies = []
    for i in range(10):
        movies.append(Movie.objects.create(
            title=f'Top Movie {i}',
            year=1990 + i,
            tmdb_id=str(2000 + i),
            vote_average=9.0 - i * 0.1,
            vote_count=5000,
        ))
    return movies


@pytest.fixture
def movies_list(db):

    movies = []
    for i in range(5):
        movies.append(Movie.objects.create(
            title=f'Test Movie {i}',
            year=2000 + i,
            tmdb_id=str(1000 + i),
            vote_average=8.0 - i * 0.5,
            vote_count=10000 - i * 1000,
            popularity=100 - i * 10,
        ))
    return movies