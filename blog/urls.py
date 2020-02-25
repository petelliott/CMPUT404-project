from django.urls import path
from . import views

urlpatterns = [
    path('homepage',views.homepage,name='homepage'),
    path('friend',views.friend,name='friend'),
    path('post',views.post,name='post'),
    path('profile',views.profile,name='profile'),
]