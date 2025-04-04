from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions, viewsets
from .permissions import IsAdminUser, IsAdminOrOwner, IsOwnerOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SuperUserCreateSerializer, OwnerListSerializer, ManagerListSerializer, ManagerCreateSerializer
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


# Role-based Permission Classes
class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_superuser


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
    permission_classes = [IsOwnerOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        data = {
            'success': True,
            'detail': 'Your account has been deactivated.',
        }
        return Response(data, status=status.HTTP_200_OK)


class SuperUserCreateView(APIView):
    permission_classes = [IsAdmin]  # Only admin users can create superusers
    serializer_class = SuperUserCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = SuperUserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.role = 'admin'  # Assign 'admin' role to superuser
            user.save()
            return Response({"detail": "Superuser created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=UserUpdateSerializer,
        responses=UserSerializer
    )
    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
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