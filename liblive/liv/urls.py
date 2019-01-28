from django.urls import path
from . import views


app_name = 'liv'
urlpatterns = [
    path('', views.IndexView, name='index'),
    path('authors/', views.AuthorView, name='authors'),
    path('author/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),
    path('books/', views.BooksView, name='books'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('genres/', views.GenresView, name='genres'),
    path('genre/<int:pk>/', views.GenreDetailView.as_view(), name='genre-detail'),
    path('update_books/', views.UpdateBooks, name='update-books'),
    path('addauthors/', views.addauthors, name='addauthors'),
    path('addgenres/', views.addgenres, name='addgenres'),
    path('addbooks/', views.addbooks, name='addbooks'),
    path('addactualbooks/', views.addactualbooks, name='addactualbooks'),
    path('getting_books/', views.getting_books, name='getting_books'),
    path('close_up/', views.close_up, name='close_up'),
    path('parse_nekrasovka/', views.parse_nekrasovka, name='parse_nekrasovka'),
    path('update_all/', views.UpdateAll, name='update_all'),
    path('delete_books/', views.delete_books, name='delete_books'),
    path('test/', views.MyView, name='test'),
]