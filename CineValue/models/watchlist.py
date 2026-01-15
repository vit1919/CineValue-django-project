from django.conf import settings
from django.db import models

from .movie import Movie


class WatchList(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="watchlist_items",
        db_index=True,
    )

    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="in_watchlists",
        db_index=True,
    )

    image_url = models.URLField(blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "movie"],
                name="unique_user_movie_watchlist",
            )
        ]
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user} → {self.movie}"
