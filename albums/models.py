from django.db import models

class Album(models.Model):
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    year = models.IntegerField()
    genre = models.CharField(max_length=100, blank=True)
    tracks = models.IntegerField(default=0)
    country = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['artist', 'year', 'title']

    def as_dict(self):
        return {
            'id': self.pk,
            'title': self.title,
            'artist': self.artist,
            'year': self.year,
            'genre': self.genre,
            'tracks': self.tracks,
            'country': self.country,
        }

    def __str__(self):
        return f"{self.title} — {self.artist} ({self.year})"
