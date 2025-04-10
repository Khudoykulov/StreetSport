from .models import Booking
from rest_framework import serializers
from django.utils import timezone
from datetime import datetime

from ..account.models import User
from ..account.serializers import UserSerializer
from ..stadiums.serializers import StadiumGetSerializer


class BookingSerializer(serializers.ModelSerializer):
    stadium = StadiumGetSerializer(read_only=True)  # Stadion haqida to‘liq ma'lumot
    user = serializers.StringRelatedField(read_only=True)  # Faqat foydalanuvchi username’i

    class Meta:
        model = Booking
        fields = ['id', 'stadium', 'user', 'booking_date', 'start_hour', 'duration']
        read_only_fields = ['user', 'stadium']  # Ushbu maydonlar faqat o‘qish uchun

    def validate(self, attrs):
        # Stadion kontekstdan olinadi yoki attrs dan
        stadium = self.context['stadium'] if 'stadium' in self.context else attrs.get('stadium')
        booking_date = attrs.get('booking_date')
        start_hour = attrs.get('start_hour')
        duration = attrs.get('duration', 1)

        # Soat 08:00-21:00 oralig‘ida bo‘lishi kerak (4 dan 24 gacha)
        if start_hour < 4 or start_hour > 24:
            raise serializers.ValidationError({"start_hour": "Boshlanish soati 08:00-21:00 oralig‘ida bo‘lishi kerak."})

        # Yakuniy soat 21:00 dan oshmasligi kerak
        end_hour = start_hour + duration
        if end_hour > 25:
            raise serializers.ValidationError({"duration": "Bron 21:00 dan keyin tugashi mumkin emas."})

        # Takroriy bronlarni tekshirish
        existing_bookings = Booking.objects.filter(
            stadium=stadium,
            booking_date=booking_date,
            is_active=True
        ).exclude(id=self.instance.id if self.instance else None)

        for booking in existing_bookings:
            existing_end = booking.start_hour + booking.duration
            new_end = start_hour + duration
            if start_hour < existing_end and new_end > booking.start_hour:
                raise serializers.ValidationError({"start_hour": "Bu vaqt oralig‘ida allaqachon bron qilingan."})

        return attrs

    def create(self, validated_data):
        user = self.context['request'].user  # Joriy foydalanuvchi
        validated_data['user'] = user
        validated_data['stadium'] = self.context['stadium']
        return super().create(validated_data)


class BookingDetailSerializer(serializers.ModelSerializer):
    stadium = StadiumGetSerializer(read_only=True)  # Stadion haqida to‘liq ma'lumot
    user = UserSerializer(read_only=True)  # Foydalanuvchi haqida to‘liq ma'lumot

    class Meta:
        model = Booking
        fields = ['id', 'stadium', 'user', 'booking_date', 'start_hour',
                  'duration', 'phone_add', 'is_active', 'created_date']
        read_only_fields = ['user', 'stadium', 'created_date']
