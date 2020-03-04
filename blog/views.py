from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django import forms
from blog import models
from django.contrib import auth
import datetime
import users.models
from blog.models import Privacy
from django.core.exceptions import PermissionDenied

class PostForm(forms.Form):
    title = forms.CharField()
    content = forms.CharField(widget=forms.Textarea)
    privacy = forms.IntegerField(widget=forms.Select(choices=(
        (Privacy.PUBLIC, "Public"),
        (Privacy.PRIVATE, "Private"),
        (Privacy.URL_ONLY, "Shareable by url only"),
        (Privacy.FRIENDS, "Friends only"),
        (Privacy.FOAF, "Friends of friends"),
    )))

def post(request):
    author = users.models.Author.from_user(request.user)
    if author is None:
        return redirect("login")

    if request.method == "POST":
        form = PostForm(request.POST)

        if form.is_valid():
            author = request.user.author

            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            privacy = form.cleaned_data["privacy"]
            post = models.Post.objects.create(date=datetime.date.today(),
                                              title=title,
                                              content=content,
                                              author=author,
                                              privacy=privacy)


            return redirect("viewpost", post_id=post.pk)
    else:
        form = PostForm()

    return render(request, "blog/post.html", {"form": form})

def viewpost(request, post_id):
    post = get_object_or_404(models.Post, pk=post_id)
    if not post.viewable_by(request.user):
        raise PermissionDenied

    return render(request, "blog/viewpost.html", {"post": post})

def allposts(request):
    return render(request, "blog/postlist.html",
                  {"posts": models.Post.objects.filter(privacy=Privacy.PUBLIC),
                   "title": "Public Posts"})

def friends(request):
    author = users.models.Author.from_user(request.user)
    if author is None:
        return redirect("login")

    return render(request, "blog/postlist.html",
                  {"posts": author.friends_posts(),
                   "title": "Friend's Posts"})
