from django.db import models
from users.models import Author, extAuthor
import polarbear.settings
import requests
import dateutil
import datetime

class Privacy:
    #TODO: private to specific author
    PRIVATE  = 0
    URL_ONLY = 1
    FRIENDS  = 2
    FOAF     = 3
    PUBLIC   = 4

def event_iter(gh):
    i = 1
    while True:
        r = requests.get("https://api.github.com/users/{}/events?page={}"\
                         .format(gh, i),
                         auth=(polarbear.settings.GH_CID,
                               polarbear.settings.GH_SECRET))

        i += 1
        if r.status_code != 200:
            break

        yield from r.json()

def update_github_posts(author):
    if author.github == None:
        return

    for i,event in enumerate(event_iter(author.github)):
        if event["type"] == "WatchEvent" or event["type"] == "RepositoryEvent":
            if Post.objects.filter(gh_event_id=event["id"]).exists():
                continue

            post = Post.objects.create(
                date=dateutil.parser.parse(
                    event['created_at']).date(),
                title="{} repository {}".format(
                    event['payload']['action'],
                    event['repo']['name']
                ),
                content="[{0}{1}]({0}{1})".format(
                    "https://github.com/",
                    event['repo']['name']),
                author=author,
                content_type="text/markdown",
                image = None,
                privacy=Privacy.PUBLIC,
                gh_event_id=event["id"])
        elif (event["type"] == "CreateEvent" and
              event["payload"]["ref_type"] == "repository"):
            post = Post.objects.create(
                date=dateutil.parser.parse(
                    event['created_at']).date(),
                title="created repository {}".format(
                    event['repo']['name']
                ),
                content="{2}\n\n[{0}{1}]({0}{1})".format(
                    "https://github.com/",
                    event['repo']['name'],
                    event['payload']['description'],
                ),
                author=author,
                content_type="text/markdown",
                image = None,
                privacy=Privacy.PUBLIC,
                gh_event_id=event["id"])


def clear_github_posts(author):
    Post.objects.filter(author=author).exclude(gh_event_id=None).delete()

# Create your models here.
class Post(models.Model):
    date         = models.DateField()
    title        = models.CharField(max_length=150)
    content      = models.CharField(max_length=8192)
    content_type = models.CharField(max_length=150)
    author       = models.ForeignKey(Author, on_delete=models.CASCADE,
                               related_name='posts')
    gh_event_id  = models.CharField(max_length=150, null=True)
    image = models.ImageField(upload_to='post_image/',blank = True)
    privacy = models.IntegerField(default=Privacy.PUBLIC)

    def viewable_by(self, user):
        if (self.privacy == Privacy.PUBLIC or
            self.privacy == Privacy.URL_ONLY):
            return True

        viewer = Author.from_user(user)

        if viewer is None:
            return False

        if self.author == viewer:
            return True

        elif self.privacy == Privacy.FRIENDS:
            return self.author.friends_with(viewer)
        elif self.privacy == Privacy.FOAF:
            #TODO
            return False

        return False


    def get_date(self):
        return self.date

    def listable_to(self, user):
        if self.privacy == Privacy.URL_ONLY:
            return self.author.user == user
        else:
            return self.viewable_by(user)

    def comment(self, author, comment):
        if isinstance(author, Author):
            return Comment.objects.create(
                date=datetime.date.today(),
                comment=comment,
                post=self,
                author=author)
        elif isinstance(author, extAuthor):
            return Comment.objects.create(
                date=datetime.date.today(),
                comment=comment,
                post=self,
                rauthor=author)
        else:
            raise TypeError("invalid author type")


    @classmethod
    def public(cls):
        return cls.objects.filter(privacy=Privacy.PUBLIC).order_by("-pk")

class Comment(models.Model):
    date    = models.DateField()
    comment = models.CharField(max_length=8192)
    post    = models.ForeignKey(Post, on_delete=models.CASCADE,
                                related_name='comments')
    author  = models.ForeignKey(Author, on_delete=models.CASCADE, null=True)
    rauthor  = models.ForeignKey(extAuthor, on_delete=models.CASCADE, null=True)
