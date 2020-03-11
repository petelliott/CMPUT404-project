from django.urls import path
from django.views.defaults import page_not_found
from . import views


urlpatterns = [
    # this view exists to name the root of the api
    path('', page_not_found, name="api_root"),
    path('author/posts', views.author_posts, name="api_authorposts"),
    path('posts', views.posts, name="api_posts"),
    path('author/<int:author_id>/posts', views.authorid_posts,
         name="api_authoridposts"),
    path('posts/<int:post_id>', views.post, name="api_post"),
    path('posts/<int:post_id>/comments', views.post_comments,
         name="api_post_comments"),
    path('author/<int:author_id>/friends', views.author_friends,
         name="api_authorfriends"),
    path('friends/<int:author_id>', views.author_friends,
         name="api_stupidalias"),
    #TODO: re type author ids, this will not work with other nodes
    path('author/<int:author_id>/friends/<int:author_id2>',
         views.author_friendswith,
         name="api_authorfriendswith"),
    path('friendrequest', views.friendrequest,
         name="api_friendrequest"),
    path('author/<int:author_id>', views.author,
         name="api_author"),
]
