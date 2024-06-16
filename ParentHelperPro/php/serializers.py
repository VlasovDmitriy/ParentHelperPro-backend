from rest_framework import serializers
from .models import User, Post, Tags, UserProfile
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer as BaseUserSerializer

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'password', 'confirm_password', 'first_name', 'last_name')

    def validate(self, data):
        if data['password'] != data.pop('confirm_password'):
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class PostSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tags.objects.all())

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