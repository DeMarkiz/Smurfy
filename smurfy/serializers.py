from rest_framework import serializers
from .models import Post, Comment, Like, Subscription


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'author', 'title', 'content', 'created_at', 'is_paid']
        read_only_fields = ['author']  # Это поле заполняется автоматически

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = self.context['request'].user

        # Если пост платный и пользователь не подписан, но он не автор, скрываем содержимое
        if instance.is_paid and not user.is_authenticated:
            representation['content'] = "Этот контент доступен только по подписке."
        elif instance.is_paid and not Subscription.objects.filter(user=user,
                                                                  post=instance).exists() and user != instance.author:
            representation['content'] = "Этот контент доступен только по подписке."

        return representation

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at']
        read_only_fields = ['post','author']

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'post', 'user']
        read_only_fields = ['post', 'user']

class SubscriptionAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'post', 'created_at', 'valid_until']
        read_only_fields = ['user', 'post']

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['user', 'post', 'valid_until']
        read_only_fields = ['user']  # Пользователь устанавливается автоматически

    def create(self, validated_data):
        # Автоматически добавляем текущего пользователя
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)