from django.shortcuts import render, redirect
from django.http import HttpResponse
from django import forms
from users import models
from django.contrib import auth

class SignupForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = auth.models.User.objects.create_user(
                username=username, password=password)
            author = models.Author.objects.create(number=60, user=user)
            auth.login(request, user)
            return redirect("auth_test")
    else:
        form = SignupForm()

    return render(request, "users/create.html", {"form": form})

def login(request):
    #TODO make seperate login and signup pages
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = auth.authenticate(request, username=username,
                                     password=password)
            if user is not None:
                auth.login(request, user)
                return redirect("auth_test")
            else:
                return redirect("login")
    else:
        form = SignupForm()

    return render(request, "users/login.html", {"form": form})

def authenticated_test(request):
    if request.user.is_authenticated:
        num = request.user.author.number
        return HttpResponse("your number is {}".format(num))
    else:
        return redirect("login")


