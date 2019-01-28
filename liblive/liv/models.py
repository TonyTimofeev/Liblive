from django.db import models
from django.contrib.auth.models import User


class Author(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class BookFromLivelib(models.Model):
    link = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Genre)
    cover = models.CharField(max_length=200)
    rating = models.FloatField()
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    linkkey = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class ActualBook(models.Model):
    author = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    notes = models.TextField()
    key = models.ForeignKey(BookFromLivelib, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
