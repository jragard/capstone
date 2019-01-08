"""overdrive URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import path
from django.contrib import admin

from overdrive.models import Book, OverdriveUser
from overdrive.views import (home_view, signup_view, login_view, logout_view,
                             content_view, mybooks_view, thanks_view,
                             return_view, hold_view)

admin.site.register(Book)
admin.site.register(OverdriveUser)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='homepage'),
    path('signup/', signup_view),
    path('login/', login_view, name='login'),
    path('logout/', logout_view),
    path('mybooks/', mybooks_view, name='mybooks'),
    path('thanks/', thanks_view),
    path('html/content/<str:url>', content_view),
    path('return/<str:url>', return_view),
    path('hold/<str:url>', hold_view),
]
