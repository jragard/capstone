from overdrive.forms import SignupForm, LoginForm
from overdrive.models import OverdriveUser, Book
from django.contrib.auth.models import User
from django.shortcuts import reverse, render, HttpResponseRedirect, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required


def home_view(request):
    books = Book.objects.all()
    books_lst = []

    for x in books:
        books_lst.append(x.title.replace(' ', '_'))

    return render(request, 'homepage.html', {'books': books,
                                             'urls': books_lst,
                                             })


def mybooks_view(request):
    current_user = OverdriveUser.objects.get(id=request.user.id)

    display_books_list = []
    books_list = []

    for book in current_user.books_checked_out.all():
        books_list.append(book.title)
        # books_list.append(book.title)

    return render(request, 'mybooks.html', {'books': books_list})


def checkout_view(request, url):
    pass


def thanks_view(request):
    title = request.POST.get('title').replace(' ', '_')
    current_user = OverdriveUser.objects.get(id=request.user.id)
    book = Book.objects.get(title=title)

    current_user.books_checked_out.add(book)
    current_user.save()

    print(current_user.books_checked_out.all())

    return render(request, 'thanks.html')


def content_view(request, url):
    html = 'checkout.html'
    content_html = 'content/' + url + '.html'

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    current_user = OverdriveUser.objects.get(id=request.user.id)
    book = Book.objects.get(title=url)

    books_list = []

    for book in current_user.books_checked_out.all():
        books_list.append(book.title)

    if url in books_list:
        return render(request, content_html)
    else:
        return render(request, html, {'title': url.replace('_', ' ')})

    if url in current_user.books_checked_out.all():
        print('yep')
        print(current_user.books_checked_out.all().first())


def signup_view(request):

    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('homepage'))

    html = 'signup.html'

    form = SignupForm(None or request.POST)

    if form.is_valid():
        data = form.cleaned_data

        user = User.objects.create_user(
            data['username'], data['email'], data['password']
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
        user = authenticate(username=data['username'], password=data['password'])

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('homepage'))

    return render(request, html, {'form': form})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('homepage'))
