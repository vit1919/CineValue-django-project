from django.conf import settings
from django.db import models

from .movie import Movie


class Rating(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ratings",
        db_index=True,
    )
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="ratings",
        db_index=True,
    )
    rating = models.PositiveSmallIntegerField()
    rated_at = models.DateTimeField(auto_now=True)
    image_url = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = "Rating"
        verbose_name_plural = "Ratings"
        unique_together = ("user", "movie")

    def __str__(self):
        return f"{self.user.username} rated {self.movie.title}: {self.rating}/10"
