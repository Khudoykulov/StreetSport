from .models import Booking
from rest_framework import serializers
from django.utils import timezone
from datetime import datetime
from ..account.serializers import UserSerializer


class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Booking
        fields = ['id', 'stadium', 'user', 'phone_add', 'booking_date', 'start_hour',
                 'duration', 'is_active', 'created_date']
        read_only_fields = ['user', 'created_date', 'is_active']

    def validate(self, data):
        """
        Bron qilish vaqtini tekshirish:
        - O‘tgan vaqtni bron qilib bo‘lmaydi.
        """
        # Joriy vaqtni olish
        now = timezone.now()

        # Bron qilinayotgan sana va vaqtni olish
        booking_date = data.get('booking_date')
        start_hour = data.get('start_hour')

        # Agar booking_date yoki start_hour bo‘lmasa, validatsiyani o‘tkazib yuboramiz
        if not booking_date or start_hour is None:
            return data

        # Bron vaqtini datetime ob'ektiga aylantirish
        booking_datetime = datetime.combine(
            booking_date,
            datetime.strptime(f"{start_hour}:00", "%H:%M").time()
        )

        # Vaqt zonasini qo‘shish (timezone-aware qilish)
        if not timezone.is_aware(booking_datetime):
            booking_datetime = timezone.make_aware(booking_datetime)

        # Agar bron vaqti hozirgi vaqtdan oldin bo‘lsa, xato chiqaramiz
        if booking_datetime < now:
            raise serializers.ValidationError(
                "O‘tgan vaqtni bron qilib bo‘lmaydi. Iltimos, kelajakdagi vaqtni tanlang."
            )

        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)