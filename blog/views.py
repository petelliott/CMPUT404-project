from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import HttpResponse
from django import forms
from blog import models
from django.contrib import auth
from django.core.exceptions import PermissionDenied
import datetime
import users.models
from blog.models import Privacy, Post
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
import commonmark
import polarbear.settings
import magic
import requests
import json
from urllib.parse import unquote
import dateutil.parser

class PostForm(forms.Form):
    title = forms.CharField()

    privacy = forms.IntegerField(widget=forms.Select(choices=(
        (Privacy.PUBLIC, "Public"),
        (Privacy.PRIVATE, "Private"),
        (Privacy.URL_ONLY, "Shareable by url only"),
        (Privacy.FRIENDS, "Friends only"),
        (Privacy.FOAF, "Friends of friends"),
    )))

    content_type = forms.CharField(widget=forms.Select(choices=(
        ("text/plain", "Plain Text"),
        ("text/markdown", "Markdown"),
        ("undefined_image_type", "Image"),
    )))
    content = forms.CharField(widget=forms.Textarea, required=False)
    image = forms.ImageField(label = 'Choose an Image', required=False)


    def __str__(self):
        post = ["Title: " + self.title,
                "Content: "+self.content,
                "privacy: "+self.privacy,
                "Image: "+self.image,
                "content_type"+self.content_type]
        return '\n'.join(post)



# Date format standarlizer,
# converting 'YYYY-MM-DDThh:mm:ss.497350-06:00' to 'YYYY-MM-DD'
def date_format_converter(date):
    if 'T' in date:
        post_date = date.split('T')[0]
    else:
        post_date = date
    return post_date



def post(request):
    author = users.models.Author.from_user(request.user)
    if author is None:
        return redirect("login")

    if request.method == "POST":
        form = PostForm(request.POST,request.FILES)

        if form.is_valid():
            author = request.user.author

            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            privacy = form.cleaned_data["privacy"]
            content_type = form.cleaned_data["content_type"]
            image = form.cleaned_data['image']

            post = models.Post.objects.create(date=datetime.date.today(),
                                              title=title,
                                              content=content,
                                              author=author,
                                              content_type=content_type,
                                              image = image,
                                              privacy=privacy)
            if post.image != None:
                image = post.image.__str__()
                mime  = magic.Magic(mime=True)
                # This function will return a mime type of this file
                post.content_type = mime.from_file(polarbear.settings.MEDIA_ROOT+image)
            post.save()

            return redirect("viewpost", post_id=post.pk)
    else:
        form = PostForm()

    return render(request, "blog/post.html", {"form": form})

def edit(request, post_id):
    """
    view to edit the post with pk=post_id
    """
    post = get_object_or_404(models.Post, pk=post_id)
    author = users.models.Author.from_user(request.user)

    if author != post.author:
        raise PermissionDenied

    if request.method == "POST":
        form = PostForm(request.POST,request.FILES)

        if form.is_valid():
            author = request.user.author

            post.title = form.cleaned_data["title"]
            post.content = form.cleaned_data["content"]
            post.privacy = form.cleaned_data["privacy"]
            post.content_type = form.cleaned_data["content_type"]
            post.image = form.cleaned_data['image']
            # Using post.save() to save our image first
            # Then we can use magic to check the mime type of image
            post.save()

            if post.image != None:
                image = post.image.__str__()
                mime  = magic.Magic(mime=True)
                # This function will return a mime type of this file
                post.content_type = mime.from_file(polarbear.settings.MEDIA_ROOT+image)

            post.save()   # Update our content_type if there is an image
            return redirect("viewpost", post_id=post.pk)
    else:
        form = PostForm(initial={"title": post.title,
                                 "content": post.content,
                                 "privacy": post.privacy,
                                 "image": post.image,
                                 "content_type": post.content_type})

    return render(request, "blog/edit.html",
                  {"form": form, "post": post})

@require_POST
def delete(request, post_id):
    post = get_object_or_404(models.Post, pk=post_id)
    author = users.models.Author.from_user(request.user)

    if author != post.author:
        raise PermissionDenied

    post.delete()
    return redirect('root')

def viewextpost(request, post_id):
    '''
    This function will renders the view post page for remote posts
    TODO: Don't think images are working properly. Should check this and fix if it doesn't work
    '''
    
    try:
        p = requests.get(unquote(post_id))
        if p.status_code == 404:
            raise Exception("Page Not Found")
        p = p.json()
    except Exception as e:
        print(e)
    post_user = auth.models.User(username=p['author']['displayName'])
    post_author = models.Author(id=p['author']['id'] ,user = post_user)
    post_date = date_format_converter(p['published'])

    # TODO: We may need to standardize the date format somehow
    post = models.Post( id     = p['source'],
                        date   = post_date,
                        title  = p['title'],
                        content= p['content'],
                        author = post_author,
                        content_type= p['contentType'])

    image_path = ''
    content = ''

    if post.content_type == "text/markdown":
        content = commonmark.commonmark(post.content)
    elif post.content_type == "text/plain":
        content = post.content
    else:
        if post.image != None:
            image = post.image.__str__()
            image_path = polarbear.settings.MEDIA_URL+image

    return render(request, "blog/viewpost.html",
                  {"post": post, "edit": False,
                   "content": content,
                   "image":  image_path})

def viewlocalpost(request, post_id):
    '''
    This function will renders the view post page for local posts
    '''
    post = get_object_or_404(models.Post, pk=post_id)
    if not post.viewable_by(request.user):
        raise PermissionDenied
    content = ''
    image_path = ''
    author = users.models.Author.from_user(request.user)

    if post.content_type == "text/markdown":
        content = commonmark.commonmark(post.content)
    elif post.content_type == "text/plain":
        content = post.content
    else:
        if post.image != None:
            image = post.image.__str__()
            image_path = polarbear.settings.MEDIA_URL+image


    return render(request, "blog/viewpost.html",
                  {"post": post, "edit": author == post.author,
                   "content": content,
                   "image":  image_path})

def viewpost(request, post_id):
    '''
    If the post id is a number, it is a local post
    Call viewextpost() if the post id is the URI of a post located on another server
    '''
    if(post_id.isdigit()):
        return viewlocalpost(request, post_id)
    else:
        return viewextpost(request, post_id)

def viewpic(request,file_name):
    file_name = "post_image/"+file_name
    post = get_object_or_404(models.Post, image=file_name)
    if not post.viewable_by(request.user):
        raise PermissionDenied

    with open(polarbear.settings.MEDIA_ROOT+file_name, "rb") as f:
        return HttpResponse(f.read(), content_type=post.content_type)




def nodeToPost(n):
    '''
    Given a Node, this function will return a list of all public posts for that node
    '''
    posts = []

    # Cheap hack until everyone has proper APIs
    if(n.service == "https://cloud-align-server.herokuapp.com"):
        # This team's API seems like it's not working right now
        # Leave this in depending on if they get their API fixed before the demo or not
        pass
        '''
        json_resp = requests.get(n.service+"/posts", headers={"Authorization":"Token d319c1aa88b6bf314faee4179b3a817ecbb9516d"}).json()

        for p in json_resp:
            post_user = auth.models.User(username=p['author_data']['displayName'])
            post_author = models.Author(id=p['author'] ,user = post_user)
            posts.append(models.Post(id=p['id'],
                                     date=p['publish'],
                                     title=p['title'],
                                     content=p['content'],
                                     author=post_author,
                                     content_type=p['contentType']))
        '''

    else:
        url = n.service+"/posts"
        json_resp = requests.get(url).json()['posts']

        for p in json_resp:
            post_user = auth.models.User(username=p['author']['displayName'])
            post_author = models.Author(id=p['author']['id'] ,user = post_user)
            post_date = dateutil.parser.parse(p['published']).date()
            posts.append(models.Post(id=p['source'],
                                     date=post_date,
                                     title=p['title'],
                                     content=p['content'],
                                     author=post_author,
                                     content_type=p['contentType']))


    return posts
    

def getPublicPosts():
    '''
    This function will return a list of all public posts from all nodes
    '''

    nodes = users.models.Node.allNodes()
    allPosts = []
    # init()
    for n in nodes:
        #if n.id == 2:
        posts = nodeToPost(n)
        allPosts += posts
        #return [s.service]
    return allPosts

def allposts(request):
    '''
    This function will get a concatenated list of all local and remote post
    the homepage will be rendered with this list of posts
    '''
    extPosts = getPublicPosts()
    # localPosts Data Format:
    # YYYY-MM-DD
    localPosts = list(models.Post.public())

    sortedPosts = (sorted(extPosts+localPosts, key=lambda x: x.get_date(),reverse = True))

    return render(request, "blog/postlist.html",
                  {"posts": sortedPosts,
                   "title": "Public Posts"})

def friends(request):
    author = users.models.Author.from_user(request.user)
    if author is None:
        return redirect("login")

    return render(request, "blog/postlist.html",
                  {"posts": author.friends_posts(),
                   "title": "Friend's Posts",
                   "fPosts": True})
