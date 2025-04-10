from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet

# router = DefaultRouter()
# router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    # path('', include(router.urls)),
    # Stadiondagi bronlar ro‘yxati va yangi bron yaratish
    path('stadiums/<int:stadium_id>/bookings/',
         BookingViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='booking-list'),

    # Bitta bronni ko‘rish, o‘zgartirish va o‘chirish
    path('stadiums/<int:stadium_id>/bookings/<int:pk>/',
         BookingViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
         name='booking-detail'),

]
