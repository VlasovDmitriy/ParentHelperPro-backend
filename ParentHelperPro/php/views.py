from django.shortcuts import render
from rest_framework import generics
from .models import User, Post
from .serializers import UserSerializer, PostSerializer


class UserAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer;


class PostAPIView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer;