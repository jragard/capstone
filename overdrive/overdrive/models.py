from django.db import models
from django.contrib.auth.models import User


class Book(models.Model):
    title = models.CharField(max_length=100)
    checked_out_count = models.IntegerField(default=0)
    hold_list = models.ManyToManyField(User)

    def __str__(self):
        return self.title


class OverdriveUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=12)
    books_checked_out = models.ManyToManyField(Book)

    def __str__(self):
        return self.username

