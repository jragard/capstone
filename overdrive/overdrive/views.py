from overdrive.forms import SignupForm, LoginForm
from overdrive.models import OverdriveUser, Book
from django.contrib.auth.models import User
from django.shortcuts import reverse, render, HttpResponseRedirect, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required


def home_view(request):
    books = Book.objects.all()
    users = OverdriveUser.objects.all()

    print(request.user.id)

    # for x in users:
    #     print(x)
    
    books_lst = []

    for x in books:
        # print(x)
        books_lst.append(x.title.replace(' ', '_'))

    print(books_lst)

    return render(request, 'homepage.html', {'books': books,
                                             'urls': books_lst,
                                             })


def content_view(request, url):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    html = 'content/' + url + '.html'
    print(html)

    return render(request, html)


def signup_view(request):

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
