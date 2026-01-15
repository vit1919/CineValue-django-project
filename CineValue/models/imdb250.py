from django.db import models


class IMDb250(models.Model):
    title = models.CharField(max_length=300)
    rank = models.IntegerField(max_length=3)
    year = models.IntegerField(null=True, blank=True)

    rating = models.FloatField(null=True, blank=True)
    duration = models.CharField(max_length=15)
    certificate = models.CharField(max_length=15, null=True, blank=True)
    genres = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    image_url = models.URLField(blank=True, null=True)
    movie_url = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "IMDb Top 250 Movie"
        verbose_name_plural = "IMDb Top 250 Movies"
        ordering = ["rank"]
        indexes = [
            models.Index(fields=["rank"]),
            models.Index(fields=["title"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.year})"
