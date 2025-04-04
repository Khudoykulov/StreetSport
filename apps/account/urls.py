from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegisterView,
    LoginAPIView,
    UserProfileRUDView,
    SuperUserCreateView,
    UserProfileAPIView,
    OwnerViewSet,
    ManagerViewSet,
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'owners', OwnerViewSet, basename='owner')
router.register(r'managers', ManagerViewSet, basename='manager')

urlpatterns = [
    path('', include(router.urls)),
    # Foydalanuvchini ro'yxatdan o'tkazish
    path('register/', UserRegisterView.as_view(), name='user-register'),

    # Login va JWT token olish
    path('login/', LoginAPIView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # Superuser yaratish (faqat adminlar)
    path('create-superuser/', SuperUserCreateView.as_view(), name='create-superuser'),

    # Profilni ko'rish, yangilash, o'chirish (RUD)
    path('profile/<int:pk>/', UserProfileRUDView.as_view(), name='user-profile-rud'),

    # Profilga kirgan foydalanuvchi uchun GET, PUT, PATCH
    path('profile/', UserProfileAPIView.as_view(), name='user-me'),
]
