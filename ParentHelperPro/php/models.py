from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.user.username


class Tags(models.Model):
    name = models.CharField(max_length=20, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Tags"


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)
    content = models.TextField()
    tags = models.ManyToManyField(Tags, related_name='posts')

    def __str__(self):
        return self.title