from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django import forms
from users import models
import blog.models
from django.contrib import auth
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db import IntegrityError
import requests
import json
from urllib.parse import unquote
from api.views import serialize_author,api_reverse
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

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

class EditProfileForm(forms.Form):
    username = forms.CharField()
    github = forms.CharField(required=False)

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

def getExtAuthorPosts(author_origin):
    '''
    Given the externalID of a Author. This function will return a lists of all Public posts for that Author
    '''
    posts = []
    posts_json = requests.get(unquote(author_origin)+"/posts").json()['posts']

    for p in posts_json:
        post_user = auth.models.User(username=p['author']['displayName'])

        post_author = models.Author(id=p['author']['id'] ,user = post_user)
        posts.append(blog.models.Post(id=p['source'], date=p['published'], title=p['title'], content=p['content'], author=post_author, content_type=p['contentType']))

    return posts

def extProfile(request, author_id):
    '''
    This function is used to render the profile of a remote Author from another server
    '''
    #TODO: Currently no code for handeling following and unfollowing Authors from other servers
    author_json = requests.get(unquote(author_id)).json()
    posts = getExtAuthorPosts(author_id)
    user = auth.models.User(username=author_json['displayName'])
    author = models.Author(id=author_json['id'] ,user = user)
    you = models.Author.from_user(request.user)
    try:
        models.extAuthor.objects.get(url = author_json['id'])
    except ObjectDoesNotExist:
        models.extAuthor.objects.create(url = author_json['id'])
    ext_friend = models.extAuthor.objects.get(url = author_json['id'])

    if request.method == 'POST':
        you = models.Author.from_user(request.user)
        if request.POST["action"] == "follow":
            # you.follow(author)
            you.follow_ext(ext_friend)

            # ----- friend request format -----
            friend_request = {}
            you_json = serialize_author(request,you)
            friend_request["query"] = "friendrequest"
            friend_request["author"] = you_json
            friend_request["friend"] = author_json
            # ----- friend request format -----
            target_url = author_json['host']+'friendrequest'
            requests.post( target_url, data=friend_request)

        elif request.POST["action"] == "un-follow":
            try:
                models.extAuthor.objects.get(url = author_json['id'])
            except ObjectDoesNotExist:
                models.extAuthor.objects.create(url = author_json['id'])
            ext_friend = models.extAuthor.objects.get(url = author_json['id'])
            you.unfollow_ext(ext_friend)

        elif request.POST["action"] == "accept-request":
            you.follow_ext(author)
            return redirect('profile', you.pk)
        elif request.POST["action"] == "reject-request":
            you.unfollow_by_ext(author)
            return redirect('profile', you.pk)
    elif request.method == 'GET':
        pass

    return render(request, "users/profile.html",
                        {"author": author,
                        "follows": you.follows(author),
                        "posts": posts,
                        #TODO: Change this to not just get friends
                        "followers": author_json['friends'],
                        "following": ext_friend.get_following(),
                        "friends": author_json['friends']})

def localProfile(request, author_id):
    '''
    This function is used to render the profile of a local Author
    '''
    author = get_object_or_404(models.Author, pk=author_id)
    you = models.Author.from_user(request.user)

    if you is None:
        return render(request, "users/profile.html", {"author": author,
                                                      "posts": author.authors_posts(request.user)})

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
        form = EditProfileForm(initial={"username": request.user.username,
                                        "github": you.github})

        return render(request, "users/profile.html",
                      {"author": author,
                       "follows": you.follows(author),
                       "freqs": you.get_friend_requests(),
                       "posts": author.authors_posts(request.user),
                       "followers": author.get_all_follower(),
                       "following": author.get_all_following(),
                       "friends": author.get_all_friend(),
                       "form": form})

def profile(request, author_id):
    '''
    If the author_id is a number, it is a local post
    Call extProfile() if the author_id is the URI of a post located on another server
    '''
    if(author_id.isdigit()):
        return localProfile(request, author_id)
    else:
        return extProfile(request, author_id)


def extFriends(request, author_id):
    '''
    This function is used to render the friends list of a remote Author
    '''

    friends = []
    author_json = requests.get(unquote(author_id)).json()

    for f in author_json['friends']:
        fUser = auth.models.User(username=f['displayName'])
        fAuthor = models.Author(id=f['id'] ,user = fUser)
        friends.append(fAuthor)

    user = auth.models.User(username=author_json['displayName'])
    author = models.Author(id=author_json['id'] ,user = user)

    return render(request, "users/friends.html",
                        {"author": author,
                        "friends": friends})



def localFriends(request, author_id):
    author = get_object_or_404(models.Author, pk=author_id)
    you = models.Author.from_user(request.user)
    remote_friends = author.get_all_remote_friend()
    remote = []
    for f in remote_friends:
        data = requests.get(f.url).json()
        remote.append((data['id'], data['displayName']))

    remote_request = author.get_remote_friend_request()
    remote_r = []
    for r in remote_request:
        data = requests.get(f.url).json()
        remote_r.append((data['id'], data['displayName']))

    return render(request, "users/friends.html",
                    {"author": author,
                    "friends": author.get_friends(),
                    "ext_friend": remote,
                    "ext_freqs": remote_r,
                    "freqs": you.get_friend_requests()})



def friends(request, author_id):
    '''
    If the author_id is a number, it is a local post
    Call extFriends() if the author_id is the URI of a post located on another server
    '''
    if(author_id.isdigit()):
        return localFriends(request, author_id)

    else:
        return extFriends(request, author_id)




def extFollowing(request, author_id):
    '''
    This function is used to render the following list of a remote Author
    '''

    following = []
    author_json = requests.get(unquote(author_id)).json()

    for f in author_json['friends']:
        fUser = auth.models.User(username=f['displayName'])
        fAuthor = models.Author(id=f['id'] ,user = fUser)
        following.append(fAuthor)

    user = auth.models.User(username=author_json['displayName'])
    author = models.Author(id=author_json['id'] ,user = user)

    return render(request, "users/following.html",
                        {"author": author,
                        #TODO: Change this to get following instead of just friends
                        "following": following})

def localFollowing(request, author_id):
    author = get_object_or_404(models.Author, pk=author_id)
    you = models.Author.from_user(request.user)
    following = author.get_all_following()
    local_f = []
    remote_f = []
    for f in following:
        if isinstance(f,int):
            friend = get_object_or_404(models.Author, pk=f)
            local_f.append(friend)
        else:
            data = requests.get(f).json()
            remote_f.append((data['id'], data['displayName']))

    return render(request, "users/following.html",
                    {"author": author,
                    "following": local_f,
                    "ext_following": remote_f})

def following(request, author_id):
    '''
    If the author_id is a number, it is a local post
    Call extFollowing() if the author_id is the URI of a post located on another server
    '''
    if(author_id.isdigit()):
        return localFollowing(request, author_id)

    else:
        return extFollowing(request, author_id)



def extFollowers(request, author_id):
    '''
    This function is used to render the followers list of a remote Author
    '''

    followers = []
    author_json = requests.get(unquote(author_id)).json()

    for f in author_json['friends']:
        fUser = auth.models.User(username=f['displayName'])
        fAuthor = models.Author(id=f['id'] ,user = fUser)
        followers.append(fAuthor)

    user = auth.models.User(username=author_json['displayName'])
    author = models.Author(id=author_json['id'] ,user = user)

    return render(request, "users/followers.html",
                        {"author": author,
                        #TODO: Change this to get followers instead of just friends
                        "followers": followers})


def localFollowers(request, author_id):
    author = get_object_or_404(models.Author, pk=author_id)
    you = models.Author.from_user(request.user)
    local_follower = author.get_followers()
    remote_follower = author.ext_follower.all()
    remote = []
    local = []
    for f in remote_follower:
        data = requests.get(f.url).json()
        remote.append((data['id'], data['displayName']))

    return render(request, "users/followers.html",
                    {"author": author,
                    "followers": local_follower,
                    "ext_follower": remote})

def followers(request, author_id):
    '''
    If the author_id is a number, it is a local post
    Call extFollowers() if the author_id is the URI of a post located on another server
    '''
    if(author_id.isdigit()):
        return localFollowers(request, author_id)
    else:
        return extFollowers(request, author_id)

@require_POST
def editProfile(request, author_id):
    author = get_object_or_404(models.Author, pk=author_id)
    you = models.Author.from_user(request.user)
    form = EditProfileForm(request.POST)

    if form.is_valid():

        try:
            request.user.username = form.cleaned_data["username"]
            request.user.save()

            newgh = form.cleaned_data["github"] or None
            if newgh != author.github:
                author.github = newgh
                author.save()
                blog.models.clear_github_posts(author)
                blog.models.update_github_posts(author)

            return redirect("profile", author_id=you.pk)
        except IntegrityError:
            return render(request, "users/profile.html",
                      {"author": author,
                       "follows": you.follows(author),
                       "freqs": you.get_friend_requests(),
                       "posts": author.authors_posts(request.user),
                       "form": form,
                       "taken": True})
