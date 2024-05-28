from django.forms import model_to_dict
from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, Post, UserProfile
from .serializers import UserSerializer, PostSerializer, UserProfileSerializer


class UserProfileDetailView(generics.RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
   # permission_classes = [permissions.AllowAny]


class UserProfileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
   # permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


class RegisterAPIView(APIView):

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserAPIDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PostAPIView(APIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response({'posts': serializer.data})

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({'post': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if not pk:
            return Response({'error': "Method PUT not allowed"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'error': "Object does not exist"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(data=request.data, instance=instance)
        if serializer.is_valid():
            serializer.save()
            return Response({"post": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
