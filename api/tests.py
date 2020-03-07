from django.test import TestCase, Client
from users.models import Author
from blog.models import Post, Privacy
import datetime
import json

# Create your tests here.
class PostsTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.author = Author.signup("author", "pw", "pw")
        self.posts = [
            Post.objects.create(date=datetime.date.today(),
                                title="a",
                                content="a",
                                author=self.author,
                                privacy=Privacy.PUBLIC),
            Post.objects.create(date=datetime.date.today(),
                                title="b",
                                content="b",
                                author=self.author,
                                privacy=Privacy.PUBLIC),
            Post.objects.create(date=datetime.date.today(),
                                title="c",
                                content="c",
                                author=self.author,
                                privacy=Privacy.PUBLIC)
        ]

    def test_metadata(self):
        j = self.c.get("/api/posts").json()

        self.assertEqual(j["query"], "posts")
        self.assertEqual(j["count"], 3)
        self.assertEqual(j["size"], 25)
        self.assertTrue("next" not in j)
        self.assertTrue("previous" not in j)
        self.assertEqual(len(j["posts"]), 3)

    def test_post_content(self):
        j = self.c.get("/api/posts").json()

        exp = self.posts[2]
        act = j["posts"][0]

        self.assertEqual(exp.title, act["title"])
        self.assertEqual("http://testserver/api/posts/{}".format(exp.pk),
                         act["source"])
        self.assertEqual("http://testserver/api/posts/{}".format(exp.pk),
                         act["origin"])
        self.assertEqual(exp.content_type, act["contentType"])
        self.assertEqual(exp.content, act["content"])
        self.assertEqual("http://testserver/api/author/{}".format(exp.author.pk),
                         act["author"]["id"])
        self.assertEqual("http://testserver/api/",
                         act["author"]["host"])
        self.assertEqual(exp.author.user.username, act["author"]["displayName"])
        self.assertEqual("http://testserver/api/author/{}".format(exp.author.pk),
                         act["author"]["url"])
        self.assertEqual(exp.pk, act["id"])
        self.assertEqual("PUBLIC", act["visibility"])
        self.assertEqual(False, act["unlisted"])
