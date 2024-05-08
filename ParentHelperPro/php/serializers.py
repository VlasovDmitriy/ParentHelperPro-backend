from rest_framework import serializers
from .models import User, Post, Tags


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'login', 'password', 'name', 'surname', 'icon')


class PostSerializer(serializers.ModelSerializer):
    tags = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ('user', 'title', 'content', 'tags')

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        post = Post.objects.create(**validated_data)
        for tag in tags:
            post.tags.add(tag)
        return post

    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.content = validated_data.get("content", instance.content)
        if 'tags' in validated_data:
            instance.tags.clear()
            for tag in validated_data.pop('tags'):
                instance.tags.add(tag)
        instance.save()
        return instance
