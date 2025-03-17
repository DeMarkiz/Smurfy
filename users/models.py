from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager


class CustomUser(AbstractUser):
    """Модель пользователя"""

    username = None

    phone = models.CharField(
        unique=True, max_length=15, verbose_name="Телефон"
    )
    city = models.CharField(max_length=30, blank=True, null=True, verbose_name="Город")
    avatar = models.ImageField(
        upload_to="avatar", blank=True, null=True, verbose_name="Аватар"
    )

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["phone"]

