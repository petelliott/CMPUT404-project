from django.db import models
from django.contrib.auth.models import User
from functools import reduce
import requests


class extAuthor(models.Model):
    url = models.URLField(max_length=200,primary_key=True)
    
    

class Author(models.Model):
    #TODO: this is where we will put friends and stuff
    number = models.IntegerField() #TODO: delete this
    friends = models.ManyToManyField('self', related_name='followers',
                                     symmetrical=False)
    
    # list of <author_id> of remote user
    ext_friends = models.ManyToManyField(extAuthor, related_name='ext_followers',
                                         symmetrical=False)
    
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='author')
    create_time = models.DateTimeField(auto_now = True)
    github = models.TextField(null = True) 

    def follow(self, other):
        self.friends.add(other)

    def unfollow(self, other):
        self.friends.remove(other)
        
    def follow_ext(self,other):
        self.ext_friends.add(other)
    
    def unfollow_ext(self,other):
        
        self.ext_friends.remove(other)
        
        
    def follows(self, other):
        try:
            if isinstance(other.id,int):
                self.friends.get(id=other.id)
            else:
                self.ext_friends.get(url=other.pk)
            return True
        except Author.DoesNotExist:
            return False
        except extAuthor.DoesNotExist:
            return False

    def friends_with(self, other):
        '''
            Check if A(self) and B(other) are friends.
            example, A.friends_with(B)
            TODO: We need this function to also get result if B is a remote user(We may need to standardize the data type)
        '''
        return self.follows(other) and other.follows(self)

    def get_friends(self):
        '''
            Get A's all local friends
            TODO: We need this function to also get A's remote friends(We may need to standardize the data type)
        '''
        return self.friends.all().intersection(self.followers.all())
    
    def get_friend_requests(self):
        '''
            Get A's all local friend requests
            TODO: We need this function to also get A's friend request from remote user
        '''
        return self.followers.all().difference(self.friends.all())

    def get_followers(self):
        '''
            Get A's all local Followers
            TODO: We need this function to also get A's remote follower(We may need to standardize the data type)
        '''
        return self.followers.all()

    def get_following(self):
        '''
            Get A's all local Followings
            TODO: We need this function to also get A's remote following(combine get_following() and get_ext_following() if possible)
            (We may need to standardize the data type)
        Return value:
            list of author model instances
        '''
        return self.friends.all()

    def get_ext_ollowing(self):
        '''
            Get A's all remote Followings
            TODO: We need this function to also get A's local following(We may need to standardize the data type)
        Return value:
            list of extAuthor model instances(URL)
        '''
        return self.ext_friends.all()

    # TODO: We need this function to also get POSTs from remote friends
    # Currently only gets post from local friends
    def friends_posts(self):
        fs = self.get_friends()
        if not fs.exists():
            return ()

        return filter(lambda p: p.listable_to(self.user),
                      reduce(
                          lambda a, b: a.union(b),
                          (a.posts.all() for a in fs)
                      ).order_by('-pk'))

    def authors_posts(self, user):
        """
        Returns all of an author's posts
        If the user is view thier own profile, all posts are returned regardless of permissions
        If viewing another author's profile, only public posts are returned
        """
        if (self.user == user):
            return self.posts.all()
        else:
            return filter( lambda p: p.listable_to(user), self.posts.all())

    def __str__(self):
        return self.user.get_username()




    @classmethod
    def from_user(cls, user):
        """
        returns a user's author, or None if it does not have one or
        isn't authenticated.
        """
        if not user.is_authenticated:
            return None

        try:
            return user.author
        except cls.DoesNotExist:
            return None

    class UserNameTaken(Exception):
        pass

    class PasswordsDontMatch(Exception):
        pass

    @classmethod
    def signup(cls, username, password1, password2):
        try:
            User.objects.get(username=username)
            raise cls.UserNameTaken()
        except User.DoesNotExist:
            pass

        if password1 != password2:
            raise cls.PasswordsDontMatch()

        user = User.objects.create_user(username=username,
                                        password=password1)
        user.is_active = False
        user.save()

        return cls.objects.create(number=60, user=user)


class Node(models.Model):
    enabled = models.BooleanField(default=True)
    service = models.URLField(max_length=250, null=True)
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='node')

    @classmethod
    def signup(cls, username, password):
        user = User.objects.create_user(username=username,
                                        password=password)
        cls.objects.create(user=user)

    @classmethod
    def from_user(cls, user):
        """
        returns a user's Node, or None if it does not have one or
        isn't authenticated.
        """
        if not user.is_authenticated:
            return None

        try:
            return user.node
        except cls.DoesNotExist:
            return None
        
    @classmethod
    def allNodes(cls):
        return cls.objects.all()
