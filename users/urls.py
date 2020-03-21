from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.signup, name="signup"),
    path('login', views.login, name="login"),
    path('logout', views.logout, name="logout"),
    path('authors/<int:author_id>',views.profile,name='profile'),
    path('authors/<str:author_origin>',views.extProfile,name='external-profile'),
    path('authors/<int:author_id>/friends',views.friends,name='friends'),
    path('authors/<int:author_id>/following',views.following,name='following'),
    path('authors/<int:author_id>/followers',views.followers,name='followers'),
    path('authors/<int:author_id>/edit',views.editProfile,name='edit-profile'),
]
