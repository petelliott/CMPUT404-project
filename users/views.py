from django.shortcuts import render
from django.http import HttpResponse
from django import forms

class SignupForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            return HttpResponse("my form worked")

    else:
        form = SignupForm()

    return render(request, "users/create.html", {"form": form})

def login(request):
    pass

def authenticated_test(request):
    return HttpResponse("you are authenticated")
