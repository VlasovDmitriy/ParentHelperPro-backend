from rest_framework import generics, status, permissions

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

import jwt
from django.conf import settings

from .models import User, Post, UserProfile
from .serializers import PostSerializer, CustomUserCreateSerializer, UserProfileSerializer
from django.shortcuts import get_object_or_404
import requests
from django.core.files.base import ContentFile




class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CustomUserCreateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserAPIDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class PostAPIView(APIView):

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


class DecodeTokenAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get('token')
        try:
            decoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_data.get('user_id')
            user = get_object_or_404(User, id=user_id)
            user_profile = get_object_or_404(UserProfile, user=user)


            return Response({'user': user.username,
                             'user_id': user_id,
                             "first_name": user.first_name,
                             "last_name": user.last_name,
                             "email": user.email,
                             "password": user.password,
                             "admin": user.is_superuser,
                             "posts": self.get_posts(user),
                             "avatar": self.get_avatar(user_profile)})
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Token has expired'}, status=401)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid token'}, status=401)

    def get_posts(self, user):

        posts = Post.objects.filter(user=user)
        serializer = PostSerializer(posts, many=True)
        print(serializer)
        return serializer.data

    def get_avatar(self, user_profile):
        serializer = UserProfileSerializer(user_profile, context={'request': self.request})
        return serializer.data['avatar']


class UserProfileView(APIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, user):
        profile = self.queryset.get(user=user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)


class UpdateAvatarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_profile = request.user.profile
        serializer = UserProfileSerializer(user_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

















