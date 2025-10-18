from django.urls import path
from django.contrib.auth import views as auth_views
from . import views



urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('search/<int:id>/', views.search_result, name='search_result'),

    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('watchlist/', views.watchlist, name='watchlist'),
    path('search/<int:id>/to_watchlist', views.to_watchlist, name='to_watchlist'),
    path('watchlist/<int:id>/remove_watchlist_movie', views.remove_watchlist_movie, name='remove_watchlist_movie'),

    path('top250_tmdb/', views.top250_tmdb, name='top250_tmdb'),
    path('search/<int:id>/remove_watchlist_movie_inresult', views.remove_watchlist_movie_inresult, name='remove_watchlist_movie_inresult'),

    path('search/<int:id>/like', views.like, name='like'),
    path('search/<int:id>/remove_liked_movie', views.remove_liked_movie, name='remove_liked_movie'),

    path('search/<int:id>/rate_movie', views.rate_movie, name='rate_movie'),
    path('users_ratings', views.users_ratings, name='users_ratings'),
    path('users_ratings/<int:id>/remove_rating', views.remove_rating, name='remove_rating'),


    
]
