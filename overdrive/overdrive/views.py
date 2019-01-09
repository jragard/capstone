from overdrive.forms import SignupForm, LoginForm
from overdrive.models import OverdriveUser, Book
from django.contrib.auth.models import User
from django.shortcuts import reverse, render, HttpResponseRedirect
from django.contrib.auth import login, authenticate, logout


def home_view(request):
    books = Book.objects.all()
    books_lst = []

    if request.user.is_authenticated:
        current_user = OverdriveUser.objects.get(id=request.user.id)
        user_books_list = [
            book.title for book in current_user.books_checked_out.all()]
        print(user_books_list)

        for book in books:
            if book.checked_out_count < 0:
                book.checked_out_count = 0
                book.save()
            print(book.hold_list.all())
            print(book.checked_out_count)

        for x in books:
            books_lst.append(x.title.replace(' ', '_'))

        return render(request, 'homepage.html', {'books': books,
                                                 'urls': books_lst,
                                                 'user_books_list': user_books_list,
                                                 })

    else:
        return render(request, 'homepage.html', {'books': books,
                                                 'urls': books_lst})


def mybooks_view(request):
    print(request.user)
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    current_user = OverdriveUser.objects.get(id=request.user.id)

    books_list = []

    for book in current_user.books_checked_out.all():
        books_list.append(book.title)

    return render(request, 'mybooks.html', {'books': books_list})


def checkout_view(request, url):
    pass


def thanks_view(request):
    title = request.POST.get('title').replace(' ', '_')
    current_user = OverdriveUser.objects.get(id=request.user.id)
    book = Book.objects.get(title=title)

    current_user.books_checked_out.add(book)
    current_user.save()

    book.checked_out_count += 1
    book.save()

    checked_out_count = book.checked_out_count
    print(checked_out_count)

    print(current_user.books_checked_out.all())

    return render(request, 'thanks.html')


def return_view(request, url):
    print(url)
    current_user = OverdriveUser.objects.get(id=request.user.id)
    book_to_return = Book.objects.get(title=url)

    hold_list = [user for user in book_to_return.hold_list.all()]
    print(len(hold_list))

    current_user.books_checked_out.remove(book_to_return)
    current_user.save()

    book_to_return.checked_out_count -= 1
    book_to_return.save()

    if len(hold_list) is not 0:
        print('-----------')
        print(hold_list[0])
        print('------------')
        user_next_in_line = OverdriveUser.objects.get(user=hold_list[0])
        user_next_in_line.books_checked_out.add(book_to_return)
        user_next_in_line.save()

        book_to_return.hold_list.remove(current_user.user)
        book_to_return.save()


    # print(current_user.books_checked_out)

    return render(request, 'return_thanks.html')


def hold_view(request, url):
    current_user = OverdriveUser.objects.get(id=request.user.id)
    book_to_hold = Book.objects.get(title=url)

    book_to_hold.hold_list.add(current_user.user)
    book_to_hold.save()
    print(book_to_hold.hold_list.all())
    return render(request, 'hold_thanks.html')


def content_view(request, url):
    html = 'checkout.html'
    content_html = 'content/' + url + '.html'
    unavailable_html = 'sorry.html'

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    current_user = OverdriveUser.objects.get(id=request.user.id)
    book = Book.objects.get(title=url)
    books_list = [bk for bk in current_user.books_checked_out.all()]

    for bk in books_list:
        if url == bk.title:
            return render(request, content_html)
    if url not in books_list and book.checked_out_count == 3:
        return render(request, unavailable_html, {'title': url.replace('_', ' '),
                                                  'url': url})
    else:
        return render(request, html, {'title': url.replace('_', ' ')})


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
        user = authenticate(
            username=data['username'], password=data['password'])

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('homepage'))

    return render(request, html, {'form': form})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('homepage'))
