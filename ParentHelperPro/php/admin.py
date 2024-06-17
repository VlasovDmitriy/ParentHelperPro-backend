from django.contrib import admin
from .models import Post, Tags, UserProfile

admin.site.register(Post)
admin.site.register(Tags)
admin.site.register(UserProfile)
