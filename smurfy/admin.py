from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Post, Comment, Like, Subscription
from users.models import CustomUser


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'is_paid')
    list_filter = ('is_paid', 'created_at')
    search_fields = ('title', 'author__phone')
    ordering = ('-created_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__phone')
    ordering = ('created_at',)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'user')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at', 'valid_until')
    list_filter = ('created_at', 'valid_until')
    search_fields = ('user__phone', 'post__title')
    ordering = ('-created_at',)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("phone", "city", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("Персональная информация", {"fields": ("city", "avatar")}),
        ("Разрешения", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
        ("Даты", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone", "password1", "password2", "is_staff", "is_active"),
        }),
    )
    search_fields = ("phone", "city")
    ordering = ("phone",)