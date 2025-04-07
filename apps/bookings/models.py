from django.db import models
from apps.account.models import User
from apps.stadiums.models import Stadium
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils import timezone


class Booking(models.Model):
    stadium = models.ForeignKey(
        Stadium,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name="Stadion"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name="Foydalanuvchi"
    )
    booking_date = models.DateField(
        verbose_name="Bron qilingan kun",
        default=timezone.now
    )
    start_hour = models.PositiveSmallIntegerField(
        choices=[(i, f"{i:02d}:00") for i in range(8, 22)],  # Operating hours 08:00-21:00
        default=12,  # Default 12:00
        verbose_name="Boshlanish soati"
    )
    duration = models.PositiveSmallIntegerField(
        default=1,  # Default 1 hour
        choices=[(i, f"{i} soat") for i in range(1, 4)],  # 1-3 hour options
        verbose_name="Davomiyligi (soat)"
    )
    phone_add = models.CharField(max_length=12,)
    is_active = models.BooleanField(default=True,verbose_name="Faol")
    created_date = models.DateTimeField(auto_now_add=True,verbose_name="Yaratilgan sana")

    class Meta:
        unique_together = ('stadium', 'booking_date', 'start_hour')
        verbose_name = "Bron"
        verbose_name_plural = "Bronlar"

    def __str__(self):
        end_hour = self.start_hour + self.duration
        return f"{self.user} - {self.stadium.name} ({self.booking_date} {self.start_hour:02d}:00-{end_hour:02d}:00)"

    def clean(self):
        """Validate booking doesn't overlap with existing bookings"""
        if not self.pk:  # Only check for new bookings
            end_hour = self.start_hour + self.duration
            overlapping = Booking.objects.filter(
                stadium=self.stadium,
                booking_date=self.booking_date,
                is_active=True
            ).filter(
                Q(start_hour__lt=end_hour) &
                Q(start_hour__gte=self.start_hour - self.duration)
            ).exclude(pk=self.pk)

            if overlapping.exists():
                raise ValidationError(
                    "Bu vaqt band qilingan. Boshqa vaqtni tanlang."
                )

            # Vaqtni to'g'ri solishtirish uchun timezone.now() dan foydalanamiz
            booking_datetime = timezone.datetime.combine(
                self.booking_date,
                timezone.datetime.strptime(f"{self.start_hour}:00", "%H:%M").time()
            )
            # Agar vaqt zonasi yo'q bo'lsa, uni qo'shamiz
            if not timezone.is_aware(booking_datetime):
                booking_datetime = timezone.make_aware(booking_datetime)

            if booking_datetime < timezone.now():
                raise ValidationError("O'tgan vaqtni bron qilib bo'lmaydi")
    def save(self, *args, **kwargs):
        self.full_clean()  # Run validation before saving
        super().save(*args, **kwargs)


class Rating(models.Model):
    stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE, related_name='ratings', verbose_name="Stadion")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    rank = models.PositiveSmallIntegerField(default=0, choices=[(i, i) for i in range(1, 11)], verbose_name="Baho")

    def __str__(self):
        return f"{self.stadium.name} - {self.rank}"


class Like(models.Model):
    stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE, related_name='likes', verbose_name="Stadion")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")

    def __str__(self):
        return f"{self.user} liked {self.stadium.name}"


class Wishlist(models.Model):
    stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE, related_name='wishlists', verbose_name="Stadion")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")

    def __str__(self):
        return f"{self.user} wishlisted {self.stadium.name}"
