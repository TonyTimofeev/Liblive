from django.urls import path
from . import views


app_name = 'liv'
urlpatterns = [
    path('', views.index_view, name='index'),
    path('authors/', views.author_view, name='authors'),
    path('author/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),
    path('books/', views.books_view, name='books'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('genres/', views.genres_view, name='genres'),
    path('genre/<int:pk>/', views.GenreDetailView.as_view(), name='genre-detail'),
    path('update_books/', views.update_books, name='update-books'),
    path('addauthors/', views.add_authors, name='add-authors'),
    path('addgenres/', views.add_genres, name='add-genres'),
    path('addbooks/', views.add_books, name='add-books'),
    path('addactualbooks/', views.add_actual_books, name='add-actual-books'),
    path('getting_books/', views.getting_books, name='getting_books'),
    path('close_up/', views.close_up, name='close_up'),
    path('parse_nekrasovka/', views.parse_nekrasovka, name='parse_nekrasovka'),
    path('update_all/', views.update_all, name='update_all'),
    path('delete_books/', views.delete_books, name='delete_books'),
    path('test/', views.MyView, name='test'),
]