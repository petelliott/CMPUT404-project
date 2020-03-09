from django.contrib import admin
from . import models

class AdminAuthor(admin.ModelAdmin):
    exclude = ("title","number",)
    list_filter = ("number",)

admin.site.register(models.Author,AdminAuthor)


