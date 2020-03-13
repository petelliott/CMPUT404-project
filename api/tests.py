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
        self.c = Client(HTTP_AUTHORIZATION="Basic YXV0aG9yOnB3")
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

    def test_update_post(self):
        post = Post.objects.create(date=datetime.date.today(),
                                   title="a",
                                   content="a",
                                   author=self.author,
                                   privacy=Privacy.PUBLIC)

        resp = self.c.put("/api/posts/{}".format(post.pk), {
            "title": "test",
        }, content_type="application/json")
        self.assertEqual(200, resp.status_code)

        post.refresh_from_db()

        self.assertEqual("test", post.title)
        self.assertEqual("a", post.content)

        resp = self.c.put("/api/posts/{}".format(post.pk), {
            "content": "test",
            "contentType": "text/markdown",
        }, content_type="application/json")
        self.assertEqual(200, resp.status_code)

        post.refresh_from_db()

        self.assertEqual("test", post.title)
        self.assertEqual("test", post.content)
        self.assertEqual("text/markdown", post.content_type)



    def test_create_post(self):
        resp = self.c.post("/api/posts", {
            "title": "test",
            "content": "f",
            "contentType": "text/plain"
        }, content_type="application/json")

        self.assertEqual(302, resp.status_code)
        self.assertTrue(resp.url.startswith("/api/posts/"))

        j = self.c.get(resp.url).json()
        self.assertEqual("test", j["title"])
        self.assertEqual("f", j["content"])
        self.assertEqual("text/plain", j["contentType"])
        self.assertEqual("PUBLIC", j["visibility"])
        self.assertEqual(False, j["unlisted"])

    def test_create_unlisted_post(self):
        resp = self.c.post("/api/posts", {
            "title": "test",
            "content": "f",
            "contentType": "text/plain",
            "unlisted": True
        }, content_type="application/json")

        self.assertEqual(302, resp.status_code)
        self.assertTrue(resp.url.startswith("/api/posts/"))

        j = self.c.get(resp.url).json()
        self.assertEqual("test", j["title"])
        self.assertEqual("f", j["content"])
        self.assertEqual("text/plain", j["contentType"])
        self.assertEqual("PUBLIC", j["visibility"])
        self.assertEqual(True, j["unlisted"])

    def test_create_private_post(self):
        resp = self.c.post("/api/posts", {
            "title": "test",
            "content": "f",
            "contentType": "text/plain",
            "visibility": "PRIVATE",
        }, content_type="application/json")

        self.assertEqual(302, resp.status_code)
        self.assertTrue(resp.url.startswith("/api/posts/"))

        j = self.c.get(resp.url).json()
        self.assertEqual("test", j["title"])
        self.assertEqual("f", j["content"])
        self.assertEqual("text/plain", j["contentType"])
        self.assertEqual("PRIVATE", j["visibility"])
        self.assertEqual(False, j["unlisted"])


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

    def test_friend2friend(self):
        j = self.c.get("/api/author/{}/friends/{}".format(
            self.author_B.pk, self.author_A.pk
        )).json()

        self.assertEqual("friends", j["query"])
        self.assertEqual(2, len(j["authors"]))
        self.assertEqual(True, j["friends"])

        j = self.c.get("/api/author/{}/friends/{}".format(
            self.author_B.pk, self.author_C.pk
        )).json()

        self.assertEqual("friends", j["query"])
        self.assertEqual(2, len(j["authors"]))
        self.assertEqual(False, j["friends"])

    def test_post_query(self):
        j = self.c.post("/api/author/{}/friends".format(self.author_A.pk), {
            "query": "friends",
            "authors": []
        }, content_type="application/json").json()

        self.assertEqual(0, len(j["authors"]))

        j = self.c.post("/api/author/{}/friends".format(self.author_A.pk), {
            "query": "friends",
            "authors": [
                "http://testserver/api/author/{}".format(self.author_B.pk)
            ]
        }, content_type="application/json").json()

        self.assertEqual(1, len(j["authors"]))
        self.assertTrue("http://testserver/api/author/{}".format(self.author_B.pk)
                        in j["authors"])

        j = self.c.post("/api/author/{}/friends".format(self.author_A.pk), {
            "query": "friends",
            "authors": [
                "http://testserver/api/author/{}".format(self.author_B.pk),
                "http://testserver/api/author/{}".format(self.author_C.pk)
            ]
        }, content_type="application/json").json()

        self.assertEqual(2, len(j["authors"]))
        self.assertTrue("http://testserver/api/author/{}".format(self.author_B.pk)
                        in j["authors"])
        self.assertTrue("http://testserver/api/author/{}".format(self.author_C.pk)
                        in j["authors"])



class AuthorPostsTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.author_A = Author.signup("author_A", "pw", "pw")
        self.author_B = Author.signup("author_B", "pw", "pw")

        self.posts = [
            Post.objects.create(date=datetime.date.today(),
                                title="a",
                                content="a",
                                author=self.author_A,
                                privacy=Privacy.PUBLIC),
            Post.objects.create(date=datetime.date.today(),
                                title="b",
                                content="b",
                                author=self.author_A,
                                privacy=Privacy.PUBLIC),
            Post.objects.create(date=datetime.date.today(),
                                title="c",
                                content="c",
                                author=self.author_B,
                                privacy=Privacy.PUBLIC)
        ]

    def test_author_posts(self):
        j = self.c.get("/api/author/{}/posts".format(self.author_A.pk)).json()

        self.assertEqual(j["count"], 2)
        self.assertEqual(len(j["posts"]), 2)
        self.assertEqual(j["posts"][0]["author"]["displayName"], "author_A")
        self.assertEqual(j["posts"][1]["author"]["displayName"], "author_A")


class FreindrequestTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.author_A = Author.signup("author_A", "pw", "pw")
        self.author_B = Author.signup("author_B", "pw", "pw")

    def test_a_follow_b(self):
        self.c.post("/api/friendrequest", {
            "query":"friendrequest",
	    "author": {
		"id":"http://testserver/api/author/{}".format(self.author_A.pk),
		"host":"http://testserver/",
		"displayName":"author_A",
		"url":"http://testserver/api/author/{}".format(self.author_A.pk)
            },
            "friend": {
		"id":"http://testserver/api/author/{}".format(self.author_B.pk),
		"host":"http://testserver/",
		"displayName":"author_B",
		"url":"http://testserver/api/author/{}".format(self.author_B.pk)
            }
        }, content_type="application/json")

        self.assertTrue(self.author_A.follows(self.author_B))
