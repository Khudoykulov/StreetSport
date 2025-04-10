# ViewSet
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Booking
from .serializers import BookingSerializer, BookingDetailSerializer
from apps.account.permissions import CustomBookingPermission
from ..account import serializers
from ..stadiums.models import Stadium
from drf_spectacular.utils import extend_schema


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all().order_by('booking_date', 'start_hour')
    permission_classes = [CustomBookingPermission]

    def get_serializer_class(self):
        # Agar bitta bron ko‘rilsa, BookingDetailSerializer ishlatiladi
        if self.action == 'retrieve':
            return BookingDetailSerializer
        # Aks holda BookingSerializer ishlatiladi
        return BookingSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Rolga qarab filtr
        if user.is_superuser or user.role == 'admin':
            pass  # Admin hamma bronlarni ko‘radi
        elif user.role == 'owner':
            queryset = queryset.filter(stadium__owner=user)  # Faqat o‘z stadionlari
        elif user.role == 'manager':
            queryset = queryset.filter(stadium__manager=user)  # Faqat boshqaradigan stadionlar
        else:
            queryset = queryset.filter(user=user)  # Oddiy foydalanuvchi o‘z bronlarini ko‘radi

        # stadium_id bo‘yicha filtr
        stadium_id = self.kwargs.get('stadium_id') or self.request.query_params.get('stadium_id')
        if stadium_id:
            queryset = queryset.filter(stadium_id=stadium_id)

        # Sana bo‘yicha filtr
        date = self.request.query_params.get('date')
        if date:
            queryset = queryset.filter(booking_date=date)

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        stadium_id = self.kwargs.get('stadium_id') or self.request.query_params.get('stadium_id')
        if stadium_id:
            try:
                stadium = Stadium.objects.get(id=stadium_id)
                context['stadium'] = stadium
            except Stadium.DoesNotExist:
                raise serializers.ValidationError({"stadium": "Bunday stadion topilmadi."})
        return context

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # Yangi bronni joriy foydalanuvchi uchun saqlash
