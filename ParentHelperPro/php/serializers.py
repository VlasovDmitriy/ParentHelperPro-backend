from django.contrib.auth.hashers import make_password, check_password
from django.core.files.base import ContentFile
from rest_framework import serializers
from .models import User, Post, UserProfile, Tags
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer as BaseUserSerializer
import requests

User = get_user_model()


class CustomUserCreateSerializer(BaseUserSerializer):
    confirm_password = serializers.CharField(write_only=True)
    secret_word = serializers.CharField(write_only=True)
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'password', 'confirm_password', 'first_name', 'last_name', 'secret_word')

    def validate(self, data):
        if data['password'] != data.pop('confirm_password'):
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        secret_word = validated_data.pop('secret_word')
        hashed_secret_word = make_password(secret_word)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )

        default_avatar_path = 'media/avatars/default_avatar.jpg'
        profile = user.profile
        profile.secret_word = hashed_secret_word
        with open(default_avatar_path, 'rb') as avatar_file:
            profile.avatar.save('default_avatar.jpg', ContentFile(avatar_file.read()), save=True)
        profile.save()
        return user


class PostSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Tags.objects.all())

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
    class Meta:
        model = UserProfile
        fields = ['avatar']

    def get_avatar(self, obj):
        request = self.context.get('request')
        avatar_url = obj.avatar.url
        return request.build_absolute_uri(avatar_url)


class PasswordResetRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    secret_word = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        secret_word = data.get('secret_word')

        try:
            user = User.objects.get(username=username)
            profile = user.profile
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid username or secret word.")

        if not check_password(secret_word, profile.secret_word):
            raise serializers.ValidationError("Invalid username or secret word.")

        return data


class PasswordResetSerializer(serializers.Serializer):
    username = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def save(self):
        username = self.validated_data['username']
        new_password = self.validated_data['new_password']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")

        user.set_password(new_password)
        user.save()


