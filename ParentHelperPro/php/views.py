
from rest_framework import generics, status, permissions

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

import jwt
from django.conf import settings

from .filter import PostFilter
from .models import User, Post, UserProfile
from .serializers import PostSerializer, CustomUserCreateSerializer, UserProfileSerializer, \
    PasswordResetRequestSerializer, UpdateUserInfoSerializer, UserProfileDetailSerializer
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend


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

    def delete(self, request, *args, **kwargs):
        pk = kwargs.get("pk", None)
        if not pk:
            return Response({'error': "Method DELETE not allowed"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'error': "Такого поста нет"}, status=status.HTTP_404_NOT_FOUND)

        post.delete()
        return Response({"message": "Пост успешно удалён"}, status=status.HTTP_200_OK)


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


class PostListFilterView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PostFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        tags = self.request.query_params.getlist('tags', None)
        title = self.request.query_params.get('title', None)

        if tags:
            for tag in tags:
                queryset = queryset.filter(tags__name=tag)

        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset


class PasswordResetRequestView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "Логин и секретное слово подтверждены, можете вводить новый пароль"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateUserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        serializer = UpdateUserInfoSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.update(request.user, serializer.validated_data)
            return Response({"message": "Данные успешно обновлены"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileByPostAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id, *args, **kwargs):
        try:
            post = Post.objects.get(id=post_id)
            user = post.user
            user_profile = UserProfile.objects.get(user=user)

            user_serializer = CustomUserCreateSerializer(user)
            profile_serializer = UserProfileSerializer(user_profile, context={'request': request})
            post_serializer = PostSerializer(user.posts.all(), many=True)

            response_data = {
                'user': user_serializer.data,
                'avatar': profile_serializer.data['avatar'],
                'posts': post_serializer.data,
                'first_name': user.first_name,
                'last_name': user.last_name
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'error': 'Пост не найден'}, status=status.HTTP_404_NOT_FOUND)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Профиль пользователя не найден'}, status=status.HTTP_404_NOT_FOUND)










