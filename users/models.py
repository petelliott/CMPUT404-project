from django.db import models
from django.contrib.auth.models import User

class Author(models.Model):
    #TODO: this is where we will put friends and stuff
    number = models.IntegerField()
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='author')
