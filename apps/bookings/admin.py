from django.contrib import admin
from .models import Booking, Rating, Like, Wishlist

# Bron qilish admin
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('stadium', 'user', 'booking_date', 'start_hour_display', 'created_date')
    list_filter = ('stadium', 'booking_date', 'start_hour')
    search_fields = ('stadium__name', 'user__username')
    ordering = ('-booking_date', '-start_hour')

    def start_hour_display(self, obj):
        return f"{obj.start_hour:02d}:00 - {obj.start_hour + 1:02d}:00"
    start_hour_display.short_description = "Bron vaqti"

# Reyting admin
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('stadium', 'user', 'rank',)
    list_filter = ('rank', 'stadium')
    search_fields = ('stadium__name', 'user__username')
    ordering = ('-rank',)

# Yoqtirish admin
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('stadium', 'user',)
    list_filter = ('stadium',)
    search_fields = ('stadium__name', 'user__username')

# Istaklar ro‘yxati admin
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('stadium', 'user',)
    list_filter = ('stadium',)
    search_fields = ('stadium__name', 'user__username')