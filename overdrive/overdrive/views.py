from overdrive.forms import SignupForm, LoginForm
from overdrive.models import OverdriveUser, Book
from django.contrib.auth.models import User
from django.shortcuts import (reverse, render, render_to_response,
                              HttpResponseRedirect, HttpResponse)
from django.contrib.auth import login, authenticate, logout
from django.db import IntegrityError
from django.views import generic

import datetime


def home_view(request):

    books = Book.objects.all()
    today = datetime.datetime.now().date()

    if request.user.is_authenticated:
        current_user = request.user.overdriveuser
        user_books_list = [book.title for book in
                           current_user.books_checked_out.all()]

        for book in books:
            if str(book.due_date) == str(today):
                current_user.books_checked_out.remove(book)
                book.checked_out_count -= 1
                book.save()
            if book.checked_out_count < 0:
                book.checked_out_count = 0
                book.save()

        return render(request, 'homepage.html',
                      {'books': books, 'user_books_list': user_books_list})

    else:
        return render(request, 'homepage.html', {'books': books,
                                                 })


def mybooks_view(request):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    current_user = request.user.overdriveuser
    books = current_user.books_checked_out.all()

    return render(request, 'mybooks.html', {'books': books
                                            })


def thanks_view(request):

    title = request.POST.get('title').replace(' ', '_')
    current_user = request.user.overdriveuser
    book = Book.objects.get(title=title)

    current_user.books_checked_out.add(book)
    book.checked_out_count += 1

    current_user.save()
    book.save()

    today = datetime.datetime.now().date()

    due = today + datetime.timedelta(14)

    book.due_date = due
    book.save()

    return render(request, 'thanks.html', {'due_date': due})


def return_view(request, url):

    current_user = request.user.overdriveuser
    book_to_return = Book.objects.get(title=url)
    hold_list = book_to_return.hold_list.all()

    current_user.books_checked_out.remove(book_to_return)
    book_to_return.checked_out_count -= 1

    current_user.save()
    book_to_return.save()

    if hold_list.count() > 0:

        user_next_in_line = OverdriveUser.objects.get(user=hold_list.first())

        user_next_in_line.books_checked_out.add(book_to_return)
        book_to_return.hold_list.remove(user_next_in_line.user)
        book_to_return.checked_out_count += 1

        user_next_in_line.save()
        book_to_return.save()

    return render(request, 'return_thanks.html')


def hold_view(request, url):

    current_user = request.user.overdriveuser
    book_to_hold = Book.objects.get(title=url)

    book_to_hold.hold_list.add(current_user.user)
    book_to_hold.save()

    return render(request, 'hold_thanks.html')


def content_view(request, url):

    html = 'checkout.html'
    content_html = 'content/' + url + '.html'
    unavailable_html = 'sorry.html'

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    current_user = request.user.overdriveuser
    book = Book.objects.get(title=url)
    books_list = [bk for bk in current_user.books_checked_out.all()]

    for bk in books_list:
        if url == bk.title:
            return render(request, content_html)
    if url not in books_list and book.checked_out_count == book.no_of_licenses:
        return render(request, unavailable_html,
                      {'title': url.replace('_', ' '),
                       'url': url,
                       'book': book
                       })
    else:
        return render(request, html, {'title': url.replace('_', ' '),
                                      'book': book
                                      })


def signup_view(request):

    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('homepage'))

    html = 'signup.html'

    form = SignupForm(None or request.POST)

    if form.is_valid():
        data = form.cleaned_data
        try:
            print ("inside signup")
            user = User.objects.create_user(
                data['username'], data['email'], data['password']
            )
        except IntegrityError:
            print ("inside signup222")
            return HttpResponse(
                'This username has already been taken. '
                'Please choose a different name.'
                '<br/> <br/>'
                '<button onClick="window.history.back()">Get Back</button>'
                )

        OverdriveUser.objects.create(
            username=data['username'],
            user=user
        )

        login(request, user)

        return HttpResponseRedirect(reverse('homepage'))

    return render(request, html, {'form': form})


def login_view(request):

    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('homepage'))

    html = 'login.html'

    form = LoginForm(None or request.POST)

    if form.is_valid():
        data = form.cleaned_data
        user = authenticate(
            username=data['username'], password=data['password'])

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('homepage'))

    return render(request, html, {'form': form})


class LogoutView(generic.View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('homepage'))


class Handler404(generic.View):
    def get(self, request, exception, template_name="404.html"):
        response = render_to_response("404.html")
        response.status_code = 404
        return response


class Handler500(generic.View):
    def get(self, request, exception, template_name="500.html"):
        response = render_to_response("500.html")
        response.status_code = 500
        return response
