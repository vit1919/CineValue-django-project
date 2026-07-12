import pytest
from CineValue.models import Movie, WatchList, Liked, Rating, IMDb250
from django.contrib.auth.models import User



@pytest.mark.django_db
def test_movie_creation(movie):
    assert movie.title == 'Myadel'
    assert movie.year == 1967
    assert movie.tmdb_id == 1241000

@pytest.mark.django_db
def test_user_creation(user):
    assert user.username == 'testuser'

@pytest.mark.django_db
def test_watchlist_item_creation(watchlist_item, user, movie):
    assert watchlist_item.user == user
    assert watchlist_item.movie == movie
    assert watchlist_item.image_url == 'https://example.com/poster.jpg'

@pytest.mark.django_db
def test_liked_item_creation(liked_item, user, movie):
    assert liked_item.user == user
    assert liked_item.movie == movie
    assert liked_item.image_url == 'https://example.com/poster.jpg'

@pytest.mark.django_db
def test_rating_item_creation(rating_item, user, movie):
    assert rating_item.user == user
    assert rating_item.movie == movie
    assert rating_item.rating == 9
    assert rating_item.image_url == 'https://example.com/poster.jpg'

