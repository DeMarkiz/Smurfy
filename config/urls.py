from django.contrib import admin
from django.urls import path, include
from users.views import RegisterView, LoginView, ProfileView, RegisterAPIView, LoginAPIView, ProfileAPIView
from smurfy.views import PostListCreateView, PostDetailView, SubscriptionPaymentView, SubscribeView

urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),

    # API пользователей
    path('api/users/', include('users.urls')),  # Маршруты для пользователей (API)
    path('api/smurfy/', include('smurfy.urls')),  # Маршруты для контента (API)

    # HTML-страницы
    path('register/', RegisterView.as_view(), name='register-html'),  # Регистрация
    path('login/', LoginView.as_view(), name='login-html'),           # Вход
    path('profile/', ProfileView.as_view(), name='profile-html'),     # Профиль
    path('posts/', PostListCreateView.as_view(), name='post-list'),  # Список постов
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail-html'),
    path('posts/<int:post_id>/subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('subscribe/pay/', SubscriptionPaymentView.as_view(), name='subscribe-pay'),

    # API-маршруты
    path('api/users/register/', RegisterAPIView.as_view(), name='api-register'),
    path('api/users/login/', LoginAPIView.as_view(), name='api-login'),
    path('api/users/profile/', ProfileAPIView.as_view(), name='api-profile'),

]