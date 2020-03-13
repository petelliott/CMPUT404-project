from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django import forms
from users import models
from django.contrib import auth
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

def toast(request):
    messages.success(request,"Sign up successully but please wait for approve")

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class SignupForm(forms.Form):
    username = forms.CharField()
    password1 = forms.CharField(widget=forms.PasswordInput,
                                label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput,
                                label="Confirm Your Password")

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            password2 = form.cleaned_data["password2"]

            try:
                author = models.Author.signup(username, password, password2)
                return render(request,"users/create.html",{"form":form,"sucess":True})
                #auth.login(request, author.user)
                return redirect("root")
            except models.Author.UserNameTaken:
                return render(request, "users/create.html",
                              {"form": form, "taken": True})
            except models.Author.PasswordsDontMatch:
                return render(request, "users/create.html",
                              {"form": form, "nomatch": True})
    else:
        form = SignupForm()

    return render(request, "users/create.html", {"form": form})

def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = auth.authenticate(request, username=username,
                                     password=password)
            if user is not None:
                auth.login(request, user)
                return redirect("root")
            else:
                return render(request, "users/login.html",
                              {"form": form, "nomatch": True})
    else:
        form = LoginForm()

    return render(request, "users/login.html", {"form": form})


@login_required
def logout(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            django_logout(request)
            return redirect("login")
    return redirect("login")


def profile(request, author_id):
    author = get_object_or_404(models.Author, pk=author_id)

    you = models.Author.from_user(request.user)
    if you is None:
        return render(request, "users/profile.html", {"author": author})

    if request.method == "POST":
        if request.POST["action"] == "follow":
            you.follow(author)
        elif request.POST["action"] == "un-follow":
            you.unfollow(author)
        elif request.POST["action"] == "accept-request":
            you.follow(author)
            return redirect('profile', you.pk)
        elif request.POST["action"] == "reject-request":
            author.unfollow(you)
            return redirect('profile', you.pk)

        return redirect('profile', author_id)
    else:
        print(you.get_friend_requests())
        return render(request, "users/profile.html",
                      {"author": author,
                       "follows": you.follows(author),
                       "freqs": you.get_friend_requests(),
                       "posts": author.authors_posts(request.user)})

def friends(request, author_id):
    author = get_object_or_404(models.Author, pk=author_id)

    return render(request, "users/friends.html",
                    {"author": author,
                     "followers": author.get_followers(),
                     "following": author.get_following()})
