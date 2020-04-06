from django.contrib import admin
from . import models


# Register your models here.
admin.site.site_header = "Admin Dashboard"
admin.site.register(models.Post)
admin.site.register(models.Comment)
