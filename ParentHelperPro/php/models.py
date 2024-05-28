
from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    followers = models.ManyToManyField(User, related_name='following', blank=True)

    def str(self):
        return self.user.username

    @property
    def followers_count(self):
        return self.followers.count()


class Tags(models.Model):
    name = models.CharField(max_length=20, db_index=True)

    def str(self):
        return self.name

    class Meta:
        verbose_name_plural = "Tags"


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)
    content = models.TextField()
    tags = models.ManyToManyField(Tags, related_name='posts')

    def str(self):
        return self.title