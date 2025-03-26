from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser
from .serializers import RegisterSerializer, UserSerializer



class LoginAPIView(APIView):
    """
    View для входа пользователя.
    Отображает страницу входа или обрабатывает POST-запрос для аутентификации.
    """
    permission_classes = [AllowAny]

    # def get(self, request):
    #     # Отображение формы входа
    #     return render(request, 'login.html')

    def post(self, request):
        # Получаем данные из запроса
        phone = request.data.get('phone')
        password = request.data.get('password')

        # Аутентификация пользователя
        user = authenticate(phone=phone, password=password)
        if user is not None:
            # Генерация JWT-токенов
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=200)
        else:
            # Ошибка аутентификации
            return Response({"error": "Неверный номер телефона или пароль"}, status=401)

class RegisterAPIView(APIView):
    """
    View для регистрации нового пользователя.
    Отображает форму регистрации или обрабатывает POST-запрос для создания пользователя.
    """
    permission_classes = [AllowAny]



    def post(self, request):
        # Обработка данных из формы регистрации
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Генерация JWT-токенов
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=201)
        return Response(serializer.errors, status=400)

class ProfileAPIView(APIView):
    """
    View для просмотра и обновления профиля пользователя.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]  # Для обработки файлов (например, аватара)

    def get(self, request):
        """
        Получение данных профиля.
        """
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def post(self, request):
        """
        Обновление данных профиля.
        """
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)




class LoginView(View):
    def post(self, request):
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        user = authenticate(phone=phone, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)

            # Сохраняем токен в сессии
            request.session['access_token'] = str(refresh.access_token)

            # Редирект на страницу профиля
            return redirect('profile')
        else:
            return render(request, 'login.html', {'error': 'Неверный номер телефона или пароль'})


class RegisterView(View):
    """
    View для регистрации пользователя через HTML-форму.
    """
    def get(self, request):
        # Отображение формы регистрации
        return render(request, 'register.html')

    def post(self, request):
        # Получаем данные из формы
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        city = request.POST.get('city', None)  # Город (необязательно)
        avatar = request.FILES.get('avatar', None)  # Аватар (необязательно)

        # Проверяем, что пользователь с таким номером телефона не существует
        if CustomUser.objects.filter(phone=phone).exists():
            return render(request, 'register.html', {'error': 'Пользователь с таким номером уже зарегистрирован'})

        # Создаем нового пользователя
        user = CustomUser.objects.create(
            phone=phone,
            password=make_password(password),  # Хэшируем пароль
            city=city,
            avatar=avatar
        )

        # Авторизуем пользователя после регистрации
        login(request, user)

        # Редирект на страницу профиля
        return redirect('profile')

class ProfileView(View):
    """
    View для просмотра и обновления профиля пользователя через HTML-форму.
    """
    @method_decorator(login_required)
    def get(self, request):
        # Отображение страницы профиля
        return render(request, 'profile.html', {'user': request.user})

    @method_decorator(login_required)
    def post(self, request):
        # Обновление данных профиля
        user = request.user
        user.city = request.POST.get('city', user.city)  # Обновляем город
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']  # Обновляем аватар
        user.save()

        # Возвращаем страницу профиля с сообщением об успешном обновлении
        return render(request, 'profile.html', {'user': user, 'message': 'Профиль успешно обновлен'})