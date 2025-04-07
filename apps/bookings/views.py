# ViewSet
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Booking
from .serializers import BookingSerializer
from apps.account.permissions import CustomBookingPermission


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all().order_by('booking_date', 'start_hour')
    serializer_class = BookingSerializer  # You'll need to create this
    permission_classes = [CustomBookingPermission]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        stadium_id = self.request.query_params.get('stadium_id')
        date = self.request.query_params.get('date')

        if stadium_id and date:
            queryset = queryset.filter(
                stadium_id=stadium_id,
                booking_date=date
            )

        return queryset

    @action(detail=False, methods=['get'])
    def available_slots(self, request):
        """Get available time slots for a stadium on a specific date"""
        stadium_id = request.query_params.get('stadium_id')
        date = request.query_params.get('date')

        if not (stadium_id and date):
            return Response(
                {"error": "stadium_id va date parametrlari kerak"},
                status=status.HTTP_400_BAD_REQUEST
            )

        booked_slots = Booking.objects.filter(
            stadium_id=stadium_id,
            booking_date=date,
            is_active=True
        ).values_list('start_hour', 'duration')

        # Generate all possible slots (8:00-21:00)
        all_slots = list(range(8, 22))  # 8:00 to 21:00
        available_slots = []

        for slot in all_slots:
            is_available = True
            for start, duration in booked_slots:
                end = start + duration
                if slot >= start and slot < end:
                    is_available = False
                    break
            if is_available:
                available_slots.append({
                    'start_hour': slot,
                    'time': f"{slot:02d}:00"
                })

        return Response(available_slots)
