from _pydatetime import timedelta
from time import timezone

from django.shortcuts import render, get_object_or_404
from django.views import View
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .models import Post, Comment, Like, Subscription
from .serializers import PostSerializer, CommentSerializer, LikeSerializer, SubscriptionSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
import stripe



class SubscriptionPaymentView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            amount = int(request.data.get('amount', 0))  # Сумма в центах
            user = request.user

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': amount,
                        'product_data': {
                            'name': 'Подписка на платный контент',
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f'http://localhost:8000/success?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url='http://localhost:8000/cancel',
                client_reference_id=str(user.id),  # Передаем ID пользователя
            )

            return Response({'url': session.url}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

"""Представления для работы с постами"""
class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        posts = Post.objects.all()
        return render(request, 'posts.html', {'posts': posts})

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)  # Сохраняем пост с автором текущего пользователя

    def get_queryset(self):
        queryset = Post.objects.all()
        is_paid = self.request.query_params.get('is_paid', None)  # Получаем параметр из URL
        if is_paid is not None:
            is_paid = is_paid.lower() == 'true'  # Преобразуем строку в булево значение
            queryset = queryset.filter(is_paid=is_paid)

        if not self.request.user.is_authenticated:
            # Для неаутентифицированных пользователей показываем только бесплатные посты
            queryset = queryset.filter(is_paid=False)
        return queryset

class PostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    # queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        post = get_object_or_404(Post, id=pk)
        return render(request, 'post_detail.html', {'post': post})

    def get_queryset(self):
        # Автор может просматривать и редактировать свои посты
        if self.request.user.is_authenticated:
            return Post.objects.filter(author=self.request.user)
        return Post.objects.none()

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

# HTML-представление для детального просмотра поста
class PostDetailView(View):
    """
    View для отображения детальной страницы поста через HTML.
    """
    def get(self, request, pk):
        post = get_object_or_404(Post, id=pk)

        # Проверка подписки для платных постов
        subscription = None
        if post.is_paid and request.user.is_authenticated:
            subscription = Subscription.objects.filter(
                user=request.user,
                post=post,
                valid_until__gt=timezone.now()
            ).first()

        if post.is_paid and not subscription:
            return render(request, 'post_detail.html', {
                'post': post,
                'subscription': False,
                'message': 'Этот контент доступен только по подписке.'
            })

        return render(request, 'post_detail.html', {
            'post': post,
            'subscription': True
        })

"""Представления для работы с комментариями"""
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Comment.objects.filter(post_id=post_id)

    def perform_create(self, serializer):
        post_id = self.kwargs['post_id'] # Получаем ID поста из URL
        post = Post.objects.get(id=post_id)  # Находим пост по ID
        serializer.save(author=self.request.user, post=post)  # Сохраняем комментарий

"""Представления для работы с лайками"""
class LikeCreateView(generics.CreateAPIView):
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        post_id = self.kwargs['post_id']  # Получаем ID поста из URL
        post = Post.objects.get(id=post_id)  # Находим пост по ID
        serializer.save(user=self.request.user, post=post)  # Сохраняем лайк

"""Представления для работы с подписками"""
class SubscriptionAPICreateView(generics.CreateAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        post_id = self.kwargs['post_id']  # Получаем ID поста из URL
        post = Post.objects.get(id=post_id)  # Находим пост по ID
        serializer.save(user=self.request.user, post=post)  # Сохраняем подписку




class SubscribeView(View):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            # Находим пост, на который хочет подписаться пользователь
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Пост не найден"}, status=status.HTTP_404_NOT_FOUND)

        # Проверяем, есть ли уже активная подписка
        subscription = Subscription.objects.filter(user=request.user, post=post).first()
        if subscription and subscription.valid_until > timezone.now():
            return Response({"message": "Вы уже подписаны на этот пост"}, status=status.HTTP_200_OK)

        # Создаем новую подписку
        serializer = SubscriptionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(post=post, valid_until=timezone.now() + timezone.timedelta(days=30))  # Подписка на 30 дней
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)