from django.db import models
from django.contrib.auth.models import User

class Author(models.Model):
    #TODO: this is where we will put friends and stuff
    number = models.IntegerField() #TODO: delete this
    friends = models.ManyToManyField('self', related_name='followers',
                                     symmetrical=False)
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='author')

    def follow(self, other):
        self.friends.add(other)

    def public_posts(self):
        pass

    def posts_for(self, user):
        pass
