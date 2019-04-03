import os
import json
import time
import requests
from .models import Author, BookFromLivelib, Genre, ActualBook
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.shortcuts import render
from bs4 import BeautifulSoup
from selenium import webdriver
from seleniumrequests import Firefox


def IndexView(request):
    current_user = request.user
    if current_user.is_anonymous:
        return render(request, 'liv/index.html')
    else:
        lob = current_user.bookfromlivelib_set.all()
        paginator = Paginator(lob, 6)
        page = request.GET.get('page')
        list_of_books = paginator.get_page(page)
        return render(request, 'liv/index.html', {'list_of_books': list_of_books})


@login_required
def AuthorView(request):
    dict_of_authors = dict()
    current_user = request.user
    for author in Author.objects.all():
        if author.bookfromlivelib_set.filter(user=current_user):
            pair = {author: [value for value in author.bookfromlivelib_set.filter(user=current_user)]}
            dict_of_authors.update(pair)
    context = {
        'dict_of_authors': dict_of_authors
    } 
    return render(request, 'liv/authors.html', context)



class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
    model = Author
    template_name = 'liv/author_detail.html'


@login_required
def BooksView(request):
    # нельзя отделять пагинатор
    current_user = request.user
    lob = current_user.bookfromlivelib_set.all()
    paginator = Paginator(lob, 15)
    page = request.GET.get('page')
    list_of_books = paginator.get_page(page)
    return render(request, 'liv/books.html', {'list_of_books': list_of_books})


class BookDetailView(LoginRequiredMixin ,generic.DetailView):
    model = BookFromLivelib
    template_name = 'liv/book_detail.html'


@login_required
def GenresView(request):
    dict_of_genres = dict()
    current_user = request.user
    for genre in Genre.objects.all().order_by('name'):
        if genre.bookfromlivelib_set.filter(user=current_user):
            pair = {genre: [value for value in genre.bookfromlivelib_set.filter(user=current_user)]}
            dict_of_genres.update(pair)
    context = {
        'dict_of_genres': dict_of_genres
    } 
    return render(request, 'liv/genres.html', context=context)


class GenreDetailView(LoginRequiredMixin ,generic.DetailView):
    model = Genre
    template_name = 'liv/genre_detail.html'


@login_required
def UpdateBooks(request):    
    return render(request, 'liv/update_books.html')


@login_required
def UpdateAll(request):
    if not os.path.exists('files_of_users'):
        os.mkdir('files_of_users')
    try:
        getting_books(request)
        close_up(request)
        parse_nekrasovka(request)
        addauthors(request)
        addgenres(request)
        addbooks(request)
        addactualbooks(request)
        delete_books(request)
        messages.success(request, 'Список обновлён')
    except:
        messages.warning(request, 'Произошла ошибка')
    return render(request, 'liv/update_books.html')


@login_required
def getting_books(request):
    links_of_books = []

    userlink = request.user.profile.link
    link = f'https://www.livelib.ru/reader/{userlink}/wish/listview/smalllist/'
    r = requests.get(link)
    soup = BeautifulSoup(r.content, 'lxml')
    
    if soup.find('a', title='Последняя страница'): 
        num_of_pages = soup.find('a', title='Последняя страница').get('href').split('~')[-1]
    else:
        num_of_pages = 1

    for page in range(int(num_of_pages)):
        # sleep против капчи
        time.sleep(2)
        page += 1
        upd_link = link + '~' + str(page)
        r = requests.get(upd_link)
        soup = BeautifulSoup(r.content, 'lxml')
        books = soup.find_all('a', class_='brow-book-name with-cycle')

        for book in books:
            links_of_books.append('https://www.livelib.ru/' + book['href'])

    with open(f'files_of_users/links_of_books_{userlink}.txt', 'w', encoding='utf-8') as f:
        for i in links_of_books:
            f.write(i + '\n')

    return render(request, 'liv/test.html')


@login_required
def close_up(request):
    webdriver = Firefox()

    userlink = request.user.profile.link

    # список для реверса
    ll = []
    with open(f'files_of_users/links_of_books_{userlink}.txt', 'r', encoding='utf-8') as f:
        if not os.path.exists(f'files_of_users/list_of_books_{userlink}.txt'):
            open(f'files_of_users/list_of_books_{userlink}.txt', 'w', encoding='utf 8').close()
        with open (f'files_of_users/list_of_books_{userlink}.txt', 'r', encoding='utf 8') as d:
            list_of_books = d.read()
            # нужен реверс, т.к. в список ссылок новые книги идут первыми, а не последними 
            for link in f: ll.append(link)
            for link in reversed(ll):
                link = link.replace('\n', '')
                if link not in list_of_books:
                    r = webdriver.request('GET', link)
                    soup = BeautifulSoup(r.content, 'lxml')

                    overview = [link]
                  
                    book = soup.find('div', class_='block-border card-block')
                    author = []
                    if book.find('h2', class_='author-name unreg'):
                        authors = book.find('h2', class_='author-name unreg')
                        names = authors.find_all('a')    
                        for name in names:
                            author.append(name.text)
                        overview.append(author)
                    else:
                        author.append('Сборник')
                        overview.append(author)
                    title = book.span.text
                    overview.append(title)
                    tags = book.find_all('a', class_='label-genre')
                    list_of_tags = []
                    for tag in tags:
                        if tag.text.startswith('№'):
                            tag = tag.text.split('в\xa0')[1]
                            list_of_tags.append(tag)
                        else:
                            list_of_tags.append(tag.text)
                    overview.append(list_of_tags)
                    cover = book.find('img', id='main-image-book')['src']
                    overview.append(cover)
                    if book.find('span', itemprop='ratingValue'):
                        rating = book.find('span', itemprop='ratingValue').text
                    else:
                        rating = 0
                    overview.append(rating)
                    description = book.p.text
                    overview.append(description)

                    data = []
                    if os.stat(f'files_of_users/list_of_books_{userlink}.txt').st_size != 0:
                        with open(f'files_of_users/list_of_books_{userlink}.txt', 'r') as f:
                            old = json.load(f)
                            for i in old:
                                data.append(i)

                    data.append(overview)
                    with open(f'files_of_users/list_of_books_{userlink}.txt', 'w') as f:
                        json.dump(data, f)

    webdriver.close()
    return render(request, 'liv/test.html')


@login_required
def parse_nekrasovka(request):
    actual_in_lib = []

    userlink = request.user.profile.link
    current_user = User.objects.get(username=request.user)

    for book in current_user.bookfromlivelib_set.all():
        author = str(book.author)
        title = book.title
        title = title.replace('(сборник)', '')
        title = title.split()
        key = book.pk

        book = '+'.join(title)
        
        url = f'http://opac.nekrasovka.ru/opacg2/?size=3&iddb=5&label0=FT&query0=&prefix1=AND&label1=TI&query1={book}&prefix2=AND&label2=AU&query2=&lang=&yearFrom=&yearTo=&_action=bibl%3Asearch%3Aadvanced'
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'lxml')

        if soup.find('table', class_='biblSearchRecordsTable id_biblSearchRecordsTableContainer'):
            tbodys = soup.find_all('tbody')
            for tbody in tbodys[1:]:
                trs = tbody.tr.find_all('td')
                author = author.split()[-1]
                if author in trs[1].text:
                    res = []
                    author = trs[1].text
                    author = author.replace('\n', '')
                    title = trs[2].text
                    title = title.replace('\n', '')
                    data = trs[3].text
                    data = data.replace('\n', '')
                    res.append(author)
                    res.append(title)
                    res.append(data)
                    res.append(key)
                    actual_in_lib.append(res)

    with open(f'files_of_users/actual_in_lib_{userlink}.txt', 'w') as f:
        json.dump(actual_in_lib, f)

    return render(request, 'liv/test.html')


@login_required
def addauthors(request):
    userlink = request.user.profile.link
    with open(f'files_of_users/list_of_books_{userlink}.txt', 'r') as f:
        data = json.load(f)
        for book in data:
            for author in book[1]:
                if not Author.objects.filter(name=author).exists():
                    a = Author()
                    a.name = author
                    a.save()
    return render(request, 'liv/test.html')


@login_required
def addgenres(request):
    userlink = request.user.profile.link
    with open(f'files_of_users/list_of_books_{userlink}.txt', 'r') as f:
        data = json.load(f)
        for book in data:
                for tag in book[3]:
                        if not Genre.objects.filter(name=tag).exists():
                            g = Genre()
                            g.name = tag
                            g.save()
    return render(request, 'liv/test.html')


@login_required
def addbooks(request):
    userlink = request.user.profile.link
    with open(f'files_of_users/list_of_books_{userlink}.txt', 'r') as f:
        data = json.load(f)
        for i in data:
            if not BookFromLivelib.objects.filter(title=i[2]).filter(author=Author.objects.get(name=i[1][0])).filter(user=User.objects.get(username=request.user)):
                b = BookFromLivelib()
                b.link = i[0]
                b.title = i[2]
                b.author = Author.objects.get(name=i[1][0])
                b.cover = i[4]
                b.rating = i[5]
                b.description = i[6]
                b.user = User.objects.get(username=request.user)
                b.save()

                # жанры добавляются после создания книги
                for g in i[3]:
                    genre = Genre.objects.get(name=g)
                    b.tags.add(genre)
                b.save()

                # ключ для str id в html
                dd = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 0: 'zero'}
                for i in list(str(b.pk)):
                    n = dd.get(int(i))
                    b.linkkey += n
                b.save()

    return render(request, 'liv/test.html')


# после добавления авторов, жанров и книг в базу
@login_required
def addactualbooks(request):
    userlink = request.user.profile.link
    with open(f'files_of_users/actual_in_lib_{userlink}.txt', 'r') as f:
        data = json.load(f)
        for i in data:
            if not ActualBook.objects.filter(title=i[1]).filter(author=i[0]).filter(notes=i[2]):
                a = ActualBook()
                a.author = i[0]
                a.title = i[1]
                a.notes = i[2]
                a.key = BookFromLivelib.objects.get(pk=i[3])
                a.user = User.objects.get(username=request.user)
                a.save()
    
    return render(request, 'liv/test.html')


@login_required
def delete_books(request):
    list_of_books = []
    userlink = request.user.profile.link
    current_user = request.user
    with open(f'files_of_users/links_of_books_{userlink}.txt', 'r', encoding='utf-8') as f:
        for i in f:
            list_of_books.append(i.strip())
    book_from_base = current_user.bookfromlivelib_set.all()
    for book in book_from_base:
        if book.link not in list_of_books:
            book.delete()
    
    return render(request, 'liv/test.html')


@login_required
def MyView(request):
    context = {
        'model': User
    }
    return render(request, 'liv/test.html', context)
