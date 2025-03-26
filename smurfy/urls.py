from django.urls import path
from .views import (PostListCreateView,
                    PostDetailView,
                    CommentListCreateView,
                    LikeCreateView,
                    SubscribeView, SubscriptionPaymentView)


urlpatterns = [
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('posts/<int:post_id>/like/', LikeCreateView.as_view(), name='like-create'),
    path('posts/<int:post_id>/subscribe/', SubscribeView.as_view(), name='subscription-create'),
    path('subscribe/pay/', SubscriptionPaymentView.as_view(), name='subscribe-pay'),
]