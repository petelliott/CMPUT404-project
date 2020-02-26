from django.shortcuts import render, redirect
from django.http import HttpResponse
from django import forms
from users import models
from django.contrib import auth
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class SignupForm(forms.Form):
    username = forms.CharField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

def signup(request):
    signup_page = True
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            password2 = form.cleaned_data["password2"]
            # Check exist:
            user = auth.authenticate(request, 
                                     username=username,
                                     password=password)
            if password2 != password:
                response = '''  <script class=" label label-danger">
                                alert("Two passwords didn't match. Please try again.");
                                location.href="/user/signup"
                                </script>
                                '''
                return HttpResponse(response)

            elif user is not None:
                auth.login(request, user)
                return redirect("auth_test")
                
            else:
                user = auth.models.User.objects.create_user(
                    username=username, password=password)
                
                author = models.Author.objects.create(number=60, user=user)
                auth.login(request, user)
                return redirect("auth_test")
    else:
        form = SignupForm()

    return render(request, "users/create.html", {"form": form})

def login(request):
    signup_page = False
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = auth.authenticate(request, username=username,
                                     password=password)
            if user is not None:
                auth.login(request, user)
                return redirect("auth_test")
            else:
                response = '''  <script class=" label label-danger">
                                alert("Your username and password didn't match. Please try again.");
                                location.href="/user/login"
                                </script>
                                '''

                return HttpResponse(response)
    else:
        form = SignupForm()

    return render(request, "users/login.html", {"form": form})


@login_required
def logout(request):
    if request.user.is_authenticated:
        django_logout(request)
        response = '''
                <p>Logout Successfully!! You will be redirected to login page in <span id="sp">1</span> seconds...</p>
                <script>

                    setInterval(go, 1000);
                    var x=0;
                    function go() {
                        if (x>=0){
                            document.getElementById("sp").innerText=x;
                        } else {
                            location.href="/user/login" ;
                        }
                        x--;
                    }
                </script>
                '''
        return HttpResponse(response)
    else:
        return redirect("login")

def authenticated_test(request):
    if request.user.is_authenticated:
        num = request.user.author.number
        response = '''
                    <p>Login/Signup Successfully!! You will be redirected to home page in <span id="sp">1</span> seconds...</p>
                    <script>

                        setInterval(go, 1000);
                        var x=0;
                        function go() {
                            if (x>=0){
                                document.getElementById("sp").innerText=x;
                            } else {
                                location.href="/blog/homepage" ;
                            }
                            x--;
                        }
                    </script>
                '''
        return HttpResponse(response)
        # return HttpResponse("your number is {}".format(num))
        # return redirect("homepage")
        # return render(request, "users/auth_test.html")
    else:
        return redirect("login")


