from django.forms import model_to_dict
from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, Post
from .serializers import UserSerializer, PostSerializer


#class PostAPIView(generics.ListAPIView):
 #   queryset = Post.objects.all()
  #  serializer_class = PostSerializer;


class UserAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer;


class PostAPIView(APIView):
    def get(self, request):
        lst = Post.objects.all().values()
        return Response({'posts': list(lst)})

    def post(self, request):
        post_new = Post.objects.create(
            user=request.data['user'],
            title=request.data['title'],
            content=request.data['content'],
            tags=request.data['tags'],

        )
        return Response({'post': model_to_dict(post_new)})

    def put(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if not pk:
            return Response({'error': "Method PUT not allowed"})

        try:
            instance = Post.oblects.get(pk=pk)
        except:
            return Response({'erorr': "Objects does not exists"})

        serializer = PostSerializer(dara=request.data, instance=instance)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"post": serializer.data})


