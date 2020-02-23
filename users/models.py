from django.db import models
from django.contrib import auth
from django.contrib.auth.models import AbstractUser

class Author(models.Model):
    #TODO: this is where we will put friends and stuff
    number = models.IntegerField()

class User(AbstractUser):
    author = models.OneToOneField(Author,
                                  on_delete=models.CASCADE,
                                  null=True)
