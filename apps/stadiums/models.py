from django.db import models
from apps.account.models import User
from django.core.exceptions import PermissionDenied

class Stadium(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nomi")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Narxi")
    description = models.TextField(null=True, blank=True, verbose_name="Tavsif")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stadiums', verbose_name="Egasi")
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_stadiums',
                                verbose_name="Menejer")
    views = models.PositiveIntegerField(default=0, verbose_name="Ko‘rishlar")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    modified_date = models.DateTimeField(auto_now=True, verbose_name="Yangilangan sana")

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)

        if user is not None:
            if user.role not in ['admin', 'owner']:
                raise PermissionDenied("Sizga ushbu amalni bajarishga ruxsat yo‘q.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        from apps.bookings.models import Rating  # Booking ilovasidan Rating modelini import qilamiz
        ratings = Rating.objects.filter(stadium=self)
        return sum(rating.rank for rating in ratings) / ratings.count() if ratings else 0


class StadiumLocation(models.Model):
    stadium = models.OneToOneField(Stadium, on_delete=models.CASCADE, related_name='location', verbose_name="Stadion")
    address = models.CharField(max_length=200, verbose_name="Manzil")
    latitude = models.CharField(max_length=50, null=True, blank=True, verbose_name="Kenglik")
    longitude = models.CharField(max_length=50, null=True, blank=True, verbose_name="Uzunlik")

    def __str__(self):
        return f"{self.stadium.name} manzili"


# Stadion rasmlari
class StadiumImage(models.Model):
    stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE, related_name='images', verbose_name="Stadion")
    image = models.ImageField(upload_to='stadiums/', verbose_name="Rasm")

    def __str__(self):
        return f"{self.stadium.name} rasmi"
