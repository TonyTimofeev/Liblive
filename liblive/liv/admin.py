from django.contrib import admin
from .models import Author,BookFromLivelib, ActualBook, Genre

admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(BookFromLivelib)
admin.site.register(ActualBook)
