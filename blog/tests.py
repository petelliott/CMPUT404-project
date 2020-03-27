from django.test import TestCase
from .models import Post, Privacy
from users.models import Author
from .util import paginate
import itertools
import datetime
import users

# Create your tests here.
class PrivacyTestCase(TestCase):
    def setUp(self):
        self.author_A = Author.signup("a", "pw", "pw")
        self.author_B = Author.signup("b", "pw", "pw")
        self.author_C = Author.signup("c", "pw", "pw")

        self.author_A.follow(self.author_B)
        self.author_B.follow(self.author_A)

        self.author_C.follow(self.author_A)

    def test_private(self):
        post = Post.objects.create(date=datetime.date.today(),
                                   title="a",
                                   content="a",
                                   author=self.author_A,
                                   privacy=Privacy.PRIVATE)

        self.assertTrue(post.viewable_by(self.author_A.user))
        self.assertFalse(post.viewable_by(self.author_B.user))
        self.assertFalse(post.viewable_by(self.author_C.user))

        self.assertTrue(post.listable_to(self.author_A.user))
        self.assertFalse(post.listable_to(self.author_B.user))
        self.assertFalse(post.listable_to(self.author_C.user))

    def test_url_only(self):
        post = Post.objects.create(date=datetime.date.today(),
                                   title="a",
                                   content="a",
                                   author=self.author_A,
                                   privacy=Privacy.URL_ONLY)

        self.assertTrue(post.viewable_by(self.author_A.user))
        self.assertTrue(post.viewable_by(self.author_B.user))
        self.assertTrue(post.viewable_by(self.author_C.user))

        self.assertTrue(post.listable_to(self.author_A.user))
        self.assertFalse(post.listable_to(self.author_B.user))
        self.assertFalse(post.listable_to(self.author_C.user))

    def test_friends(self):
        post = Post.objects.create(date=datetime.date.today(),
                                   title="a",
                                   content="a",
                                   author=self.author_A,
                                   privacy=Privacy.FRIENDS)

        self.assertTrue(post.viewable_by(self.author_A.user))
        self.assertTrue(post.viewable_by(self.author_B.user))
        self.assertFalse(post.viewable_by(self.author_C.user))

        self.assertTrue(post.listable_to(self.author_A.user))
        self.assertTrue(post.listable_to(self.author_B.user))
        self.assertFalse(post.listable_to(self.author_C.user))

    def test_foaf(self):
        #TODO
        pass

    def test_public(self):
        post = Post.objects.create(date=datetime.date.today(),
                                   title="a",
                                   content="a",
                                   author=self.author_A,
                                   privacy=Privacy.PUBLIC)

        self.assertTrue(post.viewable_by(self.author_A.user))
        self.assertTrue(post.viewable_by(self.author_B.user))
        self.assertTrue(post.viewable_by(self.author_C.user))

        self.assertTrue(post.listable_to(self.author_A.user))
        self.assertTrue(post.listable_to(self.author_B.user))
        self.assertTrue(post.listable_to(self.author_C.user))

class PaginateTestCase(TestCase):
    def test_None(self):
        l = [4,5,3,2,1,55,6,7,8,9]
        self.assertEqual(l, list(paginate(l)))

    def test_0(self):
        try:
            paginate(itertools.count(), 0, 0)
            self.fail()
        except AssertionError:
            pass

    def test_1(self):
        self.assertEqual((0,), tuple(paginate(itertools.count(), 0, 1)))
        self.assertEqual((1,), tuple(paginate(itertools.count(), 1, 1)))
        self.assertEqual((2,), tuple(paginate(itertools.count(), 2, 1)))

    def test_2(self):
        self.assertEqual((0,1), tuple(paginate(itertools.count(), 0, 2)))
        self.assertEqual((2,3), tuple(paginate(itertools.count(), 1, 2)))
        self.assertEqual((4,5), tuple(paginate(itertools.count(), 2, 2)))

    def test_3(self):
        self.assertEqual((0,1,2), tuple(paginate(itertools.count(), 0, 3)))
        self.assertEqual((3,4,5), tuple(paginate(itertools.count(), 1, 3)))
        self.assertEqual((6,7,8), tuple(paginate(itertools.count(), 2, 3)))

    def test_end(self):
        l = [0, 1, 2, 3, 4]
        self.assertEqual((3,4), tuple(paginate(l, 1, 3)))
        self.assertEqual((), tuple(paginate(l, 2, 3)))
        self.assertEqual((), tuple(paginate(l, 3, 3)))
        
        

class SpongTest(TestCase):
    # Testing Method
    def setup(self):
        self.clear()
        user = users.models.User(username = 'qianyutest3',
                                password = 'randompassword')
        user.save()
        node = users.models.Node(enabled = True,
                                service='https://spongebook.herokuapp.com',
                                user = user)
        node.save()

    def clear(self):
        nodes = users.models.Node.allNodes()
        for n in nodes:
            n.delete()
        users.models.User.objects.filter(username='qianyutest3').delete()
    
    
    def test(self):
        # TODO
        pass
    
