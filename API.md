# PolarBear API documentation

## General Usage Information

all paths for our api are prefixed with `/api`. for example, the
endpoint `/posts` would correspond to the url
`https://cmput404w20t06.herokuapp.com/api/posts`

Endpoints are authenticated with HTTP Basic auth, with one of two
types of accounts:

- **Node accounts**: accounts for specific nodes, can generally access
  anything, and act on behalf of their users. support for these will
  not be fully complete until part 2. these can be created like so

  ```
  $ ./manage.py createnode
  ```

- **Ordinary author accounts**: these have the same permissions that
    they have in the browser interface. they can be created only with
    the browser interface.


any field that is `null`, as well as comments in general, are not
implemented.


## Post Management

### GET /posts

returns a paginated list of all public posts on the server.
if there is a next or previous page, they are given by the optional
keys `"next"` and `"previous"`.


#### example

request:
```
GET /posts?page=1&size=1 HTTP/1.1
```

response:
```json
{
    "count": 9,
    "next": "http://localhost:8000/api/posts?page=2&size=1",
    "posts": [
        {
            "author": {
                "displayName": "a",
                "github": null,
                "host": "http://localhost:8000/api/",
                "id": "http://localhost:8000/api/author/1",
                "url": "http://localhost:8000/api/author/1"
            },
            "content": "5",
            "contentType": "text/plain",
            "description": null,
            "id": 12,
            "origin": "http://localhost:8000/api/posts/12",
            "published": "2020-03-11",
            "source": "http://localhost:8000/api/posts/12",
            "title": "api post",
            "unlisted": false,
            "visibility": "PUBLIC",
            "visibleTo": null
        }
    ],
    "previous": "http://localhost:8000/api/posts?page=0&size=1",
    "query": "posts",
    "size": 1
}
```

### GET /author/posts

returns a paginated list of all posts visible to the currently
authenticated user. the response will be the same as `/posts`

### GET /author/{AUTHOR_ID}/posts

returns a paginated list of all posts made by {AUTHOR_ID} visible to
the currently authenticated user. the response will be the same as
`/posts`

### GET /posts/{POST_ID}

returns the post associated with `POST_ID`

#### example

request:
```
GET /posts/1 HTTP/1.1
```

response:
```json
{
    "author": {
        "displayName": "a",
        "github": null,
        "host": "http://localhost:8000/api/",
        "id": "http://localhost:8000/api/author/1",
        "url": "http://localhost:8000/api/author/1"
    },
    "content": "newly put content",
    "contentType": "text/plain",
    "description": null,
    "id": 1,
    "origin": "http://localhost:8000/api/posts/1",
    "published": "2020-03-07",
    "source": "http://localhost:8000/api/posts/1",
    "title": "old",
    "unlisted": false,
    "visibility": "PUBLIC",
    "visibleTo": null
}
```

### PUT /posts/{POST_ID}

updates any field ("content", "contentType", "title", "unlisted",
"visibility") for the given post

#### example

request:
```json
PUT /posts/1 HTTP/1.1

{
    "title": "this is the new title",
    "content": "this is the new content",
}
```

response:
```json
{
    "author": {
        "displayName": "a",
        "github": null,
        "host": "http://localhost:8000/api/",
        "id": "http://localhost:8000/api/author/1",
        "url": "http://localhost:8000/api/author/1"
    },
    "content": "this is the new content",
    "contentType": "text/plain",
    "description": null,
    "id": 1,
    "origin": "http://localhost:8000/api/posts/1",
    "published": "2020-03-07",
    "source": "http://localhost:8000/api/posts/1",
    "title": "this is the new title",
    "unlisted": false,
    "visibility": "PUBLIC",
    "visibleTo": null
}
```
### POST /posts/

creates a new post, then redirects to it

#### example

request:
```json
PUT /posts/1 HTTP/1.1

{
    "title": "test",
    "content": "f",
    "contentType": "text/plain",
    "unlisted": false,
    "visibility": "PUBLIC",

}
```

response:
```json
HTTP/1.1 302 Found
Location: "http://localhost:8000/api/posts/5
```

## Friend Management

## Other