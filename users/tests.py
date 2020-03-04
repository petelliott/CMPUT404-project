from django.test import TestCase
from blog.models import Post, Privacy
from users.models import Author
from django.contrib.auth.models import User
import datetime

# Create your tests here.
class SignupTestCase(TestCase):
    def setUp(self):
        self.author_A = Author.signup("a", "pw", "pw")

    def test_normal_signup(self):
        a = Author.signup("b", "x", "x")
        self.assertTrue(isinstance(a, Author))

    def test_username_taken(self):
        try:
            Author.signup("a", "x", "x")
            self.fail()
        except Author.UserNameTaken:
            pass

    def test_passwords_dont_match(self):
        try:
            Author.signup("c", "x", "y")
            self.fail()
        except Author.PasswordsDontMatch:
            pass

    def test_from_user(self):
        self.assertEqual(self.author_A,
                         Author.from_user(self.author_A.user))

        user = User.objects.create_user(username="d", password="5")
        self.assertIs(None, Author.from_user(user))

class FollowTestCase(TestCase):
    def test_follow(self):
        author_A = Author.signup("a", "pw", "pw")
        author_B = Author.signup("b", "pw", "pw")

        self.assertFalse(author_A.follows(author_B))
        self.assertFalse(author_B.follows(author_A))
        self.assertFalse(author_B.friends_with(author_A))
        self.assertFalse(author_A.friends_with(author_B))

        author_A.follow(author_B)
        self.assertTrue(author_A.follows(author_B))
        self.assertFalse(author_B.follows(author_A))
        self.assertFalse(author_B.friends_with(author_A))
        self.assertFalse(author_A.friends_with(author_B))

        author_B.follow(author_A)
        self.assertTrue(author_A.follows(author_B))
        self.assertTrue(author_B.follows(author_A))
        self.assertTrue(author_B.friends_with(author_A))
        self.assertTrue(author_A.friends_with(author_B))

    def test_friends_posts(self):
        author_C = Author.signup("c", "pw", "pw")
        author_D = Author.signup("d", "pw", "pw")
        author_E = Author.signup("e", "pw", "pw")

        author_C.follow(author_D)
        author_D.follow(author_C)
        self.assertTrue(author_C.friends_with(author_D))

        cfs = list(author_C.get_friends())
        self.assertEqual(1, len(cfs))
        self.assertTrue(author_D in cfs)
        dfs = list(author_D.get_friends())
        self.assertEqual(1, len(dfs))
        self.assertTrue(author_C in dfs)

        author_C.follow(author_E)
        author_E.follow(author_C)
        self.assertTrue(author_C.friends_with(author_E))

        post_D = Post.objects.create(date=datetime.date.today(),
                                     title="a",
                                     content="a",
                                     author=author_D)

        post_E = Post.objects.create(date=datetime.date.today(),
                                     title="a",
                                     content="a",
                                     author=author_E)

        post_E_private = Post.objects.create(date=datetime.date.today(),
                                             title="a",
                                             content="a",
                                             author=author_E,
                                             privacy=Privacy.PRIVATE)

        post_D_url = Post.objects.create(date=datetime.date.today(),
                                         title="a",
                                         content="a",
                                         author=author_D,
                                         privacy=Privacy.URL_ONLY)

        fps = list(author_C.friends_posts())
        self.assertEqual(2, len(fps))
        self.assertTrue(post_D in fps)
        self.assertTrue(post_E in fps)
