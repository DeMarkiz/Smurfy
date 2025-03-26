from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'phone', 'city', 'avatar']
        read_only_fields = ['id']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Пароль не возвращается в ответе

    class Meta:
        model = CustomUser
        fields = ['phone', 'password', 'city', 'avatar']
        extra_kwargs = {
            'password': {'write_only': True},  # Пароль не возвращается в ответе
            'city': {'required': False},      # Город необязателен
            'avatar': {'required': False},    # Аватар необязателен
        }

    def create(self, validated_data):
        user = CustomUser.objects.create(
            phone=validated_data['phone'],
            password=make_password(validated_data['password']),
            city=validated_data.get('city', None),  # Используем .get() с fallback на None
            avatar=validated_data.get('avatar', None)  # Используем .get() с fallback на None
        )
        return user

















# from rest_framework import serializers
# from .models import CustomUser
#
# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = ['id', 'phone', 'city', 'avatar']
#         read_only_fields = ['id']
#
# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)   # password
#
#     class Meta:
#         model = CustomUser
#         fields = ['phone', 'city', 'avatar', 'password']
#
#     def create(self, validated_data):
#         user = CustomUser.objects.create_user(
#             phone=validated_data['phone'],
#             password=validated_data['password'], # set password during creation
#             city = validated_data.get('city'),  # Используем .get() с None по умолчанию
#             avatar = validated_data.get('avatar'),
#
#         )
#         return user