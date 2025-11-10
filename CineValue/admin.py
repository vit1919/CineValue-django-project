from django.contrib import admin
from .models import Movie, IMDb250, WatchList, Liked, Rating


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'year', 'vote_average', 'popularity')
    search_fields = ('title', 'original_title')
    list_filter = ('year', 'adult')


@admin.register(IMDb250)
class IMDb250Admin(admin.ModelAdmin):
    list_display = ('rank', 'title', 'year', 'rating')
    search_fields = ('title',)
    list_filter = ('year',)
    ordering = ('rank',)


@admin.register(WatchList)
class WatchListAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'added_at')
    search_fields = ('user__username', 'movie__title')
    list_filter = ('added_at',)


@admin.register(Liked)
class LikedAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'added_at')
    search_fields = ('user__username', 'movie__title')
    list_filter = ('added_at',)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'rating', 'rated_at')
    search_fields = ('user__username', 'movie__title')
    list_filter = ('rating', 'rated_at')




