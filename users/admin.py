from django.contrib import admin
from . import models

class AdminAuthor(admin.ModelAdmin):
    exclude = ("title","number",)
    list_filter = ("create_time","number",)

admin.site.register(models.Author,AdminAuthor)
admin.site.register(models.Node)

