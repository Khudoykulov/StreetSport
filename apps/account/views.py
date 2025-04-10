from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions, viewsets
from rest_framework.generics import UpdateAPIView
from .permissions import IsAdminUser, IsAdminOrOwner, IsAdminOrReadOnly, IsAdminOrSelf
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SuperUserCreateSerializer, OwnerListSerializer, ManagerListSerializer, ManagerCreateSerializer, \
    UserRoleUpdateSerializer, ResetPasswordSerializer, ChangePasswordSerializer, UserListSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from apps.account.models import User, UserToken
from apps.account.serializers import (
    UserRegisterSerializer,
    UserProfileSerializer,
    CustomTokenObtainPairSerializer,
    SuperUserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
    OwnerCreateSerializer,
)


class UserRegisterView(generics.GenericAPIView):
    serializer_class = UserRegisterSerializer
    queryset = User.objects.all()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Assign role based on user input or default
        role = request.data.get('role', 'user')  # Default 'user' role
        user.role = role
        user.save()

        # Create user token
        token = UserToken.objects.create(user=user)

        # Send activation code (simulated as a message)
        # ecommerce_send_email.apply_async(("Activation Token Code", str(token.token), [user.phone]), )
        data = {
            'success': True,
            'detail': 'Activation Token Code has been sent to your phone.',
        }
        return Response(data, status=status.HTTP_201_CREATED)


class LoginAPIView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserProfileRUDView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserProfileSerializer
    queryset = User.objects.filter(is_active=True)
    permission_classes = [IsAdminOrSelf]
    parser_classes = [MultiPartParser, FormParser]

    # PUT metodini disable qilish va Swaggerda ko‘rsatmaslik
    @extend_schema(exclude=True)  # drf-spectacular uchun PUT ni Swaggerdan o‘chirish
    def put(self, request, *args, **kwargs):
        return Response(
            {'error': 'PUT method is not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        data = {
            'success': True,
            'detail': 'Your account has been permanently deleted.',
        }
        return Response(data, status=status.HTTP_200_OK)


class SuperUserCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]  # faqat admin huquqga ega
    serializer_class = SuperUserCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = SuperUserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.role = 'admin'  # Assign 'admin' role to superuser
            user.save()
            return Response({"detail": "Superuser created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OwnerViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(role='owner')
    serializer_class = OwnerListSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]  # ✅ Faqat admin qo‘shadi

    def get_serializer_class(self):
        if self.action == 'create':
            return OwnerCreateSerializer
        return OwnerListSerializer

    def perform_create(self, serializer):
        # `role` va `created_by` ni bu yerda qo‘shib saqlaymiz
        serializer.save(role='owner', created_by=self.request.user)


class ManagerViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(role='manager')
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def get_serializer_class(self):
        if self.action == 'create':
            return ManagerCreateSerializer
        return ManagerListSerializer

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return User.objects.filter(role='manager')
        elif self.request.user.role == 'owner':
            return User.objects.filter(role='manager', created_by=self.request.user)
        return User.objects.none()

    def perform_create(self, serializer):
        # Menejer yaratilganda created_by ga joriy foydalanuvchini qo‘shish
        serializer.save(created_by=self.request.user)


class UserRoleUpdateView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRoleUpdateSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated, IsAdminUser]  # Faqat admin o‘zgartira oladi

    # PUT metodini disable qilish va Swaggerda ko‘rsatmaslik
    @extend_schema(exclude=True)  # drf-spectacular uchun PUT ni Swaggerdan o‘chirish
    def put(self, request, *args, **kwargs):
        return Response(
            {'error': 'PUT method is not allowed.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @extend_schema(
        summary="User foydalanuvchilarni owner ga o‘zgartirish",
        description="Faqat admin 'user' rolidagi foydalanuvchilarni 'owner' ga o‘zgartirishi mumkin.",
        responses={
            200: dict(
                type='object',
                properties={
                    'success': dict(type='boolean', description='Muvaffaqiyat holati'),
                    'detail': dict(type='string', description='Xabar'),
                }
            ),
            400: dict(
                type='object',
                properties={
                    'error': dict(type='object', description='Xatolik tafsilotlari'),
                }
            ),
            404: dict(
                type='object',
                properties={
                    'detail': dict(type='string', description='Xatolik xabari'),
                }
            )
        }
    )
    def update(self, request, *args, **kwargs):
        instance = self.get_object()  # Yangilanayotgan foydalanuvchi

        # Agar foydalanuvchi 'user' emas bo‘lsa, xatolik qaytarish (qo‘shimcha tekshiruv)
        if instance.role != 'user':
            return Response(
                {'detail': "Faqat 'user' rolidagi foydalanuvchilarni 'owner' ga o‘zgartirish mumkin."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(
                {'success': True, 'detail': f"User role updated to {instance.role}."},
                status=status.HTTP_200_OK
            )
        return Response(
            {'error': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSelf]

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {
            'success': True,
            'detail': 'Your password has been changed.',
        }
        return Response(data, status=status.HTTP_200_OK)


class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSelf]

    @extend_schema(
        summary="Parolni yangilash",
        description="Foydalanuvchi o‘z parolini yoki admin boshqa foydalanuvchining parolini yangilay oladi. Admin uchun 'user_id' ixtiyoriy.",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'user_id': {'type': 'integer', 'description': 'Foydalanuvchi ID (faqat admin uchun)'},
                    'password': {'type': 'string', 'description': 'Yangi parol'},
                    'password2': {'type': 'string', 'description': 'Yangi parol tasdiqlash'},
                },
                'required': ['password', 'password2'],
            }
        },
        responses={
            200: dict(
                type='object',
                properties={
                    'success': dict(type='boolean'),
                    'detail': dict(type='string'),
                }
            ),
            400: dict(
                type='object',
                properties={
                    'detail': dict(type='string'),
                }
            )
        }
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {
            'success': True,
            'detail': 'Your password has been reset.',
        }
        return Response(data, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="Foydalanuvchilar ro‘yxatini olish",
        description="Faqat admin foydalanuvchilar uchun mavjud. Barcha foydalanuvchilar ro‘yxatini qaytaradi."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UserStatsView(APIView):
    permission_classes = [IsAdminUser]  # Faqat admin ko‘ra oladi

    @extend_schema(
        summary="Foydalanuvchilar statistikasi",
        description="Umumiy foydalanuvchilar soni va rollar bo‘yicha statistikani qaytaradi. Faqat admin uchun.",
        responses={
            200: dict(
                type='object',
                properties={
                    'total_users': dict(type='integer', description='Umumiy foydalanuvchilar soni'),
                    'owners': dict(type='integer', description='Ownerlar soni'),
                    'managers': dict(type='integer', description='Managerlar soni'),
                    'users': dict(type='integer', description='Oddiy foydalanuvchilar soni'),
                }
            )
        }
    )
    def get(self, request, *args, **kwargs):
        # Umumiy foydalanuvchilar soni

        # Rollarga ko‘ra sonlar
        owners = User.objects.filter(role='owner').count()
        managers = User.objects.filter(role='manager').count()
        users = User.objects.filter(role='user').count()
        total_users = owners + managers + users

        # Javob ma’lumotlari
        data = {
            'total_users': total_users,
            'owners': owners,
            'managers': managers,
            'users': users,
        }

        return Response(data, status=status.HTTP_200_OK)
