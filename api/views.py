from django.shortcuts import render
from django.http import JsonResponse
from django.urls import reverse
from blog.util import paginate
import blog

def auth_api(func):
    def inner(request):
        #TODO: authenticate with HTTP basic auth
        return func(request)

    return inner

@auth_api
def author_posts(request):
    #TODO: maybe authors can use the api?
    #      until then it's the same as posts
    return posts()

DEFAULT_PAGE_SIZE = 25

def api_reverse(request, path, **kwargs):
    return request.build_absolute_uri(reverse(path, kwargs=kwargs))

def serialize_post(request, post):
    return {
        "title": post.title,
        "source": api_reverse(request, "api_post", post_id=post.pk),
        "origin": api_reverse(request, "api_post", post_id=post.pk),
        "description": None, #TODO
        "contentType": post.content_type,
        "content": post.content, #TODO: images
        "author": {
            "id": api_reverse(request, "api_author",
                              author_id=post.author.pk),
            "host": api_reverse(request, "api_root"),
            "displayName": post.author.user.username,
            "url": api_reverse(request, "api_author",
                               author_id=post.author.pk),
            "github": None #TODO
        },
        #TODO: comments
    }


@auth_api
def posts(request):
    page = int(request.GET.get("page", 0))
    size = int(request.GET.get("size", DEFAULT_PAGE_SIZE))

    public = blog.models.Post.public()
    total = public.count()

    posts = list(paginate(public, page, size))
    return JsonResponse({
        "query": "posts",
        "count": total,
        "size": size,
        #TODO: next and previous
        "posts": [serialize_post(request, p) for p in posts]
    })


def authorid_posts(request, author_id):
    pass


def post(request, post_id):
    pass


def post_comments(request, post_id):
    pass


def author_friends(request, author_id):
    pass


def author_friendswith(request, author_id, author_id2):
    pass


def friendrequest(request):
    pass


def author(request, author_id):
    pass
