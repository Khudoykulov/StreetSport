from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegisterView,
    LoginAPIView,
    UserProfileRUDView,
    SuperUserCreateView,
    OwnerViewSet,
    ManagerViewSet,
    UserRoleUpdateView,
    ResetPasswordView,
    ChangePasswordView, UserListView, UserStatsView
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'owners', OwnerViewSet, basename='owner')
router.register(r'managers', ManagerViewSet, basename='manager')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('create-superuser/', SuperUserCreateView.as_view(), name='create-superuser'),
    path('profile/<int:pk>/', UserProfileRUDView.as_view(), name='user-profile-rud'),
    path('update-role/<int:pk>/', UserRoleUpdateView.as_view(), name='update-user-role'),
    path('password/change/', ChangePasswordView.as_view(), name='password-change'),
    path('password/reset/', ResetPasswordView.as_view(), name='password-reset'),
    path('users/', UserListView.as_view(), name='user-list'),  # Foydalanuvchilar ro‘yxati
    path('user-stats/', UserStatsView.as_view(), name='user-stats'),  # Statistika endpointi
]
