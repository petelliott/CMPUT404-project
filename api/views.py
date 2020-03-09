from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from blog.util import paginate
from blog.models import Privacy, Post
from users.models import Author
import blog

def auth_api(func):
    def inner(request, *args, **kwargs):
        #TODO: authenticate with HTTP basic auth
        return func(request, *args, **kwargs)

    return inner

@auth_api
def author_posts(request):
    #TODO: maybe authors can use the api?
    #      until then it's the same as posts
    return posts()

DEFAULT_PAGE_SIZE = 25

def api_reverse(request, path, **kwargs):
    return request.build_absolute_uri(reverse(path, kwargs=kwargs))


def serialize_author(request, author):
    return {
        "id": api_reverse(request, "api_author",
                          author_id=author.pk),
        "host": api_reverse(request, "api_root"),
        "displayName": author.user.username,
        "url": api_reverse(request, "api_author",
                           author_id=author.pk),
        "github": None #TODO
    }

def serialize_post(request, post):
    visibility_table = {
        Privacy.PRIVATE: "PRIVATE",
        Privacy.URL_ONLY: "PUBLIC",
        Privacy.FRIENDS: "FRIENDS",
        Privacy.FOAF: "FOAF",
        Privacy.PUBLIC: "PUBLIC",
    }
    return {
        "title": post.title,
        "source": api_reverse(request, "api_post", post_id=post.pk),
        "origin": api_reverse(request, "api_post", post_id=post.pk),
        "description": None, #TODO
        "contentType": post.content_type,
        "content": post.content, #TODO: images
        "author": serialize_author(request, post.author),
        #TODO: comments
        "published": post.date,
        "id": post.pk,
        "visibility": visibility_table[post.privacy],
        "visibleTo": None,
        "unlisted": post.privacy == Privacy.URL_ONLY
    }


@auth_api
def posts(request):
    page = int(request.GET.get("page", 0))
    size = int(request.GET.get("size", DEFAULT_PAGE_SIZE))

    public = blog.models.Post.public()
    total = public.count()

    def pageurl(n):
        return "{}?page={}&size={}".format(
            api_reverse(request, "api_posts"),
            n, size)

    nex = {"next": pageurl(page+1) } if (page+1)*size < total else {}
    prev = {"previous": pageurl(page-1) } if page > 0 else {}

    posts = list(paginate(public, page, size))
    return JsonResponse({
        "query": "posts",
        "count": total,
        "size": size,
        **nex,
        **prev,
        "posts": [serialize_post(request, p) for p in posts]
    })


@auth_api
def authorid_posts(request, author_id):
    author = get_object_or_404(Author, pk=author_id)

    page = int(request.GET.get("page", 0))
    size = int(request.GET.get("size", DEFAULT_PAGE_SIZE))

    # TODO: for future parts this will be augemented to check viewer
    #       permissions. currently this behavior is not specified
    public = author.posts.filter(privacy=Privacy.PUBLIC).order_by("-pk")
    total = public.count()

    def pageurl(n):
        return "{}?page={}&size={}".format(
            api_reverse(request, "api_authoridposts", author_id=author_id),
            n, size)

    nex = {"next": pageurl(page+1) } if (page+1)*size < total else {}
    prev = {"previous": pageurl(page-1) } if page > 0 else {}

    posts = list(paginate(public, page, size))
    return JsonResponse({
        "count": total,
        "size": size,
        **nex,
        **prev,
        "posts": [serialize_post(request, p) for p in posts]
    })


@auth_api
def post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    return JsonResponse(serialize_post(request, post))


@auth_api
def post_comments(request, post_id):
    pass


@auth_api
def author_friends(request, author_id):
    author = get_object_or_404(Author, pk=author_id)
    if request.method == "POST":
        #TODO will be added in part 2
        pass
    else:
        return JsonResponse({
            "query": "friends",
            "authors": [
                api_reverse(request, "api_author",
                            author_id=a.pk)
                for a in author.get_friends()
            ],
        })


@auth_api
def author_friendswith(request, author_id, author_id2):
    pass


@auth_api
def friendrequest(request):
    pass


@auth_api
def author(request, author_id):
    author = get_object_or_404(Author, pk=author_id)
    return JsonResponse({
        **serialize_author(request, author),
        "friends": [serialize_author(request, f)
                    for f in author.get_friends()]
    })
