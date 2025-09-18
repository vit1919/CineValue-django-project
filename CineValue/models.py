from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=500)
    original_title = models.CharField(max_length=500, null=True, blank=True)
    original_language = models.CharField(max_length=15, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    overview = models.TextField(null=True, blank=True)

    tmdb_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    imdb_id = models.CharField(max_length=20, unique=True, null=True, blank=True)

    status = models.CharField(max_length=50, null=True, blank=True)
    release_date = models.DateTimeField(max_length=20, null=True, blank=True)
    
    adult = models.BooleanField(default=False)
    budget = models.BigIntegerField(null=True, blank=True)
    revenue = models.IntegerField(null=True, blank=True)

    genres = models.CharField(max_length=500, blank=True)

    vote_average = models.FloatField(null=True, blank=True)
    vote_count = models.IntegerField(null=True, blank=True)
    popularity = models.FloatField(null=True, blank=True)

    poster_path = models.CharField(max_length=200, blank=True, null=True)
    backdrop_path = models.CharField(max_length=200, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    production_countries = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.year})"

    class Meta:
        ordering = ['-vote_count', '-vote_average']
        verbose_name = 'Movie'
        verbose_name_plural = 'Movies'


