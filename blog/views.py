from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django import forms
from blog import models
from django.contrib import auth
from django.core.exceptions import PermissionDenied
import datetime
import users.models

def friend(request):
    return render(request,"blog/friend.html" )


class PostForm(forms.Form):
    title = forms.CharField()
    content = forms.CharField(widget=forms.Textarea)

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
            post = models.Post.objects.create(date=datetime.date.today(),
                                              title=title,
                                              content=content,
                                              author=author)


            return redirect("viewpost", post_id=post.pk)
    else:
        form = PostForm()

    return render(request, "blog/post.html", {"form": form})

def edit(request, post_id):
    """
    view to edit the post with pk=post_id
    """
    post = get_object_or_404(models.Post, pk=post_id)
    author = users.models.Author.from_user(request.user)

    if author != post.author:
        raise PermissionDenied

    if request.method == "POST":
        form = PostForm(request.POST)

        if form.is_valid():
            author = request.user.author

            post.title = form.cleaned_data["title"]
            post.content = form.cleaned_data["content"]
            post.save()

            return redirect("viewpost", post_id=post.pk)
    else:
        form = PostForm(initial={"title": post.title,
                                 "content": post.content})

    return render(request, "blog/edit.html",
                  {"form": form, "post": post})


def viewpost(request, post_id):
    #TODO: post view permissions
    post = get_object_or_404(models.Post, pk=post_id)
    return render(request, "blog/viewpost.html", {"post": post})

def allposts(request):
    #TODO: authenticate posts
    return render(request, "blog/postlist.html",
                  {"posts": models.Post.objects.all()})

def profile(request):
    return render(request, "blog/profile.html" )
