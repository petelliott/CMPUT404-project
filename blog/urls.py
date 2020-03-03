from django.urls import path
from . import views

urlpatterns = [
    path('post',views.post,name='post'),
    path('post/<int:post_id>', views.viewpost, name='viewpost'),
    path('posts/all', views.allposts, name='allposts'),
    path('posts/friends', views.friends, name='friendposts'),
]
