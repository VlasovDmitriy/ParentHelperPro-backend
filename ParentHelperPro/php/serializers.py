from rest_framework import serializers
from .models import User, Post, Tags


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'login', 'password', 'name', 'surname', 'icon')

    def create(self, validated_data):
        user = User.objects.create(
            login=validated_data['login'],
            password=validated_data['password'],
            name=validated_data['name'],
            surname=validated_data['surname'],
            icon=validated_data['icon']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


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
