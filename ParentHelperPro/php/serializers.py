from django.core.files.base import ContentFile
from rest_framework import serializers
from .models import User, Post, UserProfile
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer as BaseUserSerializer
import requests

User = get_user_model()


class CustomUserCreateSerializer(BaseUserSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'password', 'confirm_password', 'first_name', 'last_name')

    def validate(self, data):
        if data['password'] != data.pop('confirm_password'):
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        photo_url = validated_data.pop('photo_url', None)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        if photo_url:
            response = requests.get(photo_url)
            if response.status_code == 200:
                avatar_file = ContentFile(response.content)
                avatar_file_name = f'avatars/{user.username}.jpg'
                user.profile.avatar.save(avatar_file_name, avatar_file, save=True)
        return user


class PostSerializer(serializers.ModelSerializer):
    tags = serializers.StringRelatedField(many=True)

    class Meta:
        model = Post
        fields = ('id','user', 'title', 'content', 'tags')

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        post = Post.objects.create(**validated_data)
        post.tags.set(tags)
        return post

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        instance.title = validated_data.get("title", instance.title)
        instance.content = validated_data.get("content", instance.content)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['user', 'avatar']

    def get_avatar(self, obj):
        request = self.context.get('request')
        avatar_url = obj.avatar.url
        return request.build_absolute_uri(avatar_url)
