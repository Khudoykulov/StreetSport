from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions, viewsets
from rest_framework.generics import UpdateAPIView
from .permissions import IsAdminUser, IsAdminOrOwner, IsReadOnly, IsAdminOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SuperUserCreateSerializer, OwnerListSerializer, ManagerListSerializer, ManagerCreateSerializer,UserRoleUpdateSerializer
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
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        data = {
            'success': True,
            'detail': 'Your account has been permanently deleted.',
        }
        return Response(data, status=status.HTTP_200_OK)


class SuperUserCreateView(APIView):
    permission_classes = [IsAdminUser]  # Only admin users can create superusers
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
    permission_classes = [IsAdminUser]  # ✅ Faqat admin qo‘shadi

    def get_serializer_class(self):
        if self.action == 'create':
            return OwnerCreateSerializer
        return OwnerListSerializer

    def perform_create(self, serializer):
        serializer.save(role='owner')  # Automatik owner rolini beradi


class ManagerViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(role='manager')
    serializer_class = ManagerListSerializer
    permission_classes = [IsAdminOrOwner]  # ✅ Admin va Owner qo‘shishi mumkin

    def get_serializer_class(self):
        if self.action == 'create':
            return ManagerCreateSerializer
        return ManagerListSerializer

    def perform_create(self, serializer):
        serializer.save(role='manager')  # Automatik manager rolini beradi


class UserRoleUpdateView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRoleUpdateSerializer
    permission_classes = [permissions.IsAdminUser]  # Admin tomonidan faqat o'zgartirilishi kerak

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        role = request.data.get('role')

        # Faqat valid ro'lni qo'llash
        if role and role in dict(User.ROLE_CHOICES):
            instance.role = role
            instance.save()
            return Response({'success': True, 'detail': f"User role updated to {role}."}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid role provided.'}, status=status.HTTP_400_BAD_REQUEST)