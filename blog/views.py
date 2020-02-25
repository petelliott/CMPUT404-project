from django.shortcuts import render, redirect
from django.http import HttpResponse
from django import forms
from django.contrib import auth

def homepage(request):

    return render(request, "blog/homepage.html" )

def friend(request):

    return render(request,"blog/friend.html" )

def post(request):

    return render(request,"blog/post.html" )

def profile(request):

    return render(request, "blog/profile.html" )