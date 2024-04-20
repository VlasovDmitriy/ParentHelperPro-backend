from django.contrib import admin
from .models import User, Post, Tags

admin.site.register(User)
admin.site.register(Post)
admin.site.register(Tags)
