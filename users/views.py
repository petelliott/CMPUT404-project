from django.shortcuts import render, redirect
from django.http import HttpResponse
from django import forms
from users import models

class SignupForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            author = models.Author.objects.create(number=60)
            models.User.objects.create_user(
                username=username, password=password, author=author)
            return redirect("auth_test")
    else:
        form = SignupForm()

    return render(request, "users/create.html", {"form": form})

def login(request):
    pass

def authenticated_test(request):

    return HttpResponse("you are authenticated")
