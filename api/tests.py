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

    def test_pagnation(self):
        j = self.c.get("/api/posts").json()
        self.assertTrue("next" not in j)
        self.assertTrue("previous" not in j)
        self.assertEqual(3, len(j["posts"]))

        j = self.c.get("/api/posts?page=0&size=2").json()
        self.assertEqual("http://testserver/api/posts?page=1&size=2", j["next"])
        self.assertTrue("previous" not in j)
        self.assertEqual(2, len(j["posts"]))

        j = self.c.get("/api/posts?page=1&size=2").json()
        self.assertTrue("next" not in j)
        self.assertEqual("http://testserver/api/posts?page=0&size=2",
                         j["previous"])
        self.assertEqual(1, len(j["posts"]))


class ViewAuthorTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.author_A = Author.signup("author_A", "pw", "pw")
        self.author_B = Author.signup("author_B", "pw", "pw")
        self.author_C = Author.signup("author_C", "pw", "pw")

        self.author_A.follow(self.author_B)
        self.author_B.follow(self.author_A)
        self.author_A.follow(self.author_C)
        self.author_C.follow(self.author_A)

    def test_author(self):
        j = self.c.get("/api/author/{}".format(self.author_A.pk)).json()

        self.assertEqual(
            "http://testserver/api/author/{}".format(self.author_A.pk),
            j["id"])
        self.assertEqual("http://testserver/api/", j["host"])
        self.assertEqual(self.author_A.user.username, j["displayName"])
        self.assertEqual(
            "http://testserver/api/author/{}".format(self.author_A.pk),
            j["url"])
        self.assertEqual(2, len(j["friends"]))


class PostTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.author = Author.signup("author", "pw", "pw")
        self.post = Post.objects.create(date=datetime.date.today(),
                                        title="a",
                                        content="a",
                                        author=self.author,
                                        privacy=Privacy.PUBLIC)

    def test_post(self):
        j = self.c.get("/api/posts/{}".format(self.post.pk)).json()

        exp = self.post
        act = j

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


class AuthorFriendsTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.author_A = Author.signup("author_A", "pw", "pw")
        self.author_B = Author.signup("author_B", "pw", "pw")
        self.author_C = Author.signup("author_C", "pw", "pw")

        self.author_A.follow(self.author_B)
        self.author_B.follow(self.author_A)
        self.author_A.follow(self.author_C)
        self.author_C.follow(self.author_A)

    def test_A_friends(self):
        j = self.c.get("/api/author/{}/friends".format(self.author_A.pk)).json()

        self.assertEqual("friends", j["query"])
        self.assertEqual(2, len(j["authors"]))
        self.assertTrue("http://testserver/api/author/{}".format(self.author_B.pk)
                        in j["authors"])
        self.assertTrue("http://testserver/api/author/{}".format(self.author_C.pk)
                        in j["authors"])

    def test_B_friends(self):
        j = self.c.get("/api/author/{}/friends".format(self.author_B.pk)).json()

        self.assertEqual("friends", j["query"])
        self.assertEqual(1, len(j["authors"]))
        self.assertTrue("http://testserver/api/author/{}".format(self.author_A.pk)
                        in j["authors"])
