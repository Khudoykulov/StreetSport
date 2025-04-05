from django.db import models
from apps.account.models import User
from apps.stadiums.models import Stadium

# Bron qilish
class Booking(models.Model):
    stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE, related_name='bookings', verbose_name="Stadion")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', verbose_name="Foydalanuvchi")
    booking_date = models.DateField(verbose_name="Bron qilingan kun")
    start_hour = models.PositiveSmallIntegerField(
        choices=[(i, f"{i:02d}:00") for i in range(0, 24)],
        verbose_name="Boshlanish soati"
    )
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")

    def __str__(self):
        return f"{self.user} - {self.stadium.name} ({self.booking_date} {self.start_hour}:00-{self.start_hour + 1}:00)"

    class Meta:
        unique_together = ('stadium', 'booking_date', 'start_hour')

# Reyting
class Rating(models.Model):
    stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE, related_name='ratings', verbose_name="Stadion")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")
    rank = models.PositiveSmallIntegerField(default=0, choices=[(i, i) for i in range(1, 11)], verbose_name="Baho")

    def __str__(self):
        return f"{self.stadium.name} - {self.rank}"

# Yoqtirish
class Like(models.Model):
    stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE, related_name='likes', verbose_name="Stadion")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")

    def __str__(self):
        return f"{self.user} liked {self.stadium.name}"

# Istaklar ro‘yxati
class Wishlist(models.Model):
    stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE, related_name='wishlists', verbose_name="Stadion")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Foydalanuvchi")

    def __str__(self):
        return f"{self.user} wishlisted {self.stadium.name}"