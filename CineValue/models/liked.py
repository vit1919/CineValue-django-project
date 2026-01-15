from django.conf import settings
from django.db import models

from .movie import Movie


class Liked(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="liked_items",
        db_index=True,
    )
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="in_liked",
        db_index=True,
    )
    added_at = models.DateTimeField(auto_now_add=True)
    image_url = models.URLField(blank=True, null=True)

    class Meta:
        unique_together = ("user", "movie")
        verbose_name = "Liked Movie"
        verbose_name_plural = "Liked Movies"

    def __str__(self):
        return f"{self.user.username} liked {self.movie.title}"
