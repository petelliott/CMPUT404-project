from django.db import models
from users.models import Author

# Create your models here.
class Post(models.Model):
    date = models.DateField()
    title = models.CharField(max_length=150)
    content = models.CharField(max_length=8192)
    markdown = models.BooleanField(default=False)
    author = models.ForeignKey(Author, on_delete=models.CASCADE,
                               related_name='posts')
