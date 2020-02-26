from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django import forms
from blog import models
from django.contrib import auth
import datetime
import users.models

def homepage(request):

    return render(request, "blog/homepage.html" )

def friend(request):

    return render(request,"blog/friend.html" )


class PostForm(forms.Form):
    title = forms.CharField()
    content = forms.CharField(widget=forms.Textarea)

def post(request):
    if not request.user.is_authenticated:
        return redirect("login")

    try:
        author = request.user.author
    except users.models.Author.DoesNotExist:
        return redirect("login")

    if request.method == "POST":
        form = PostForm(request.POST)

        if form.is_valid():
            author = request.user.author

            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            models.Post.objects.create(date=datetime.date.today(),
                                       title=title,
                                       content=content,
                                       author=author)


            return redirect("auth_test") #TODO: redirect to created post
    else:
        form = PostForm()

    return render(request, "blog/post.html", {"form": form})

def viewpost(request, post_id):
    #TODO: post view permissions
    post = get_object_or_404(models.Post, pk=post_id)
    return render(request, "blog/viewpost.html", {"post": post})

def profile(request):

    return render(request, "blog/profile.html" )
