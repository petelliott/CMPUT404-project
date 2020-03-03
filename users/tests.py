from django.test import TestCase
from blog.models import Post, Privacy
from users.models import Author
from django.contrib.auth.models import User

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
