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
    
]
