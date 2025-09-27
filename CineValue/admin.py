from django.contrib import admin
from .models import Movie


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):

    list_display = ['id', 'title', 'year', 'tmdb_id']
    list_filter = ['id', 'title', 'tmdb_id']
    search_fields = ['title']




