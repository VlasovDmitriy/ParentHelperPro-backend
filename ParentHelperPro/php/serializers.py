from rest_framework import serializers
from .models import User, Post, Tags, UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name')




class UserProfileSerializer(serializers.ModelSerializer):
    followers_count = serializers.ReadOnlyField()
    followers = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ('avatar', 'followers_count', 'followers', 'following_count', 'following')

    def get_following_count(self, obj):
        return obj.user.following.count()

    def get_following(self, obj):
        return [profile.user.username for profile in obj.user.following.all()]

    def get_followers(self, obj):
        return [user.username for user in obj.followers.all()]


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
