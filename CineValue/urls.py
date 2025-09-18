from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('search/<int:id>/', views.search_result, name='search_result'),
    
]
