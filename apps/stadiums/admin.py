from django.contrib import admin
from .models import Stadium, StadiumLocation, StadiumImage, Rating, Like, Wishlist


# Stadion rasmlarini inline tarzda ko‘rsatish uchun
class StadiumImageInline(admin.TabularInline):
    model = StadiumImage
    extra = 1
    fields = ('image',)
    # readonly_fields = ('image',)


# Stadion joylashuvini inline tarzda ko‘rsatish uchun
class StadiumLocationInline(admin.StackedInline):
    model = StadiumLocation
    extra = 0
    fields = ('address', 'latitude', 'longitude')


# Stadion admin
@admin.register(Stadium)
class StadiumAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'price',
        'owner',
        'manager',
        'views',  # Ko‘rishlar faqat ko‘rinadi, tahrirlanmaydi
        'average_rating',
        'likes_count',
        'wishlist_count',
        'bookings_count',
        'images_count',
        'created_date'
    )
    list_filter = ('owner', 'manager', 'created_date')
    search_fields = ('name', 'description')
    inlines = [StadiumLocationInline, StadiumImageInline]
    list_editable = ('price',)  # Faqat narxni tahrirlash mumkin
    readonly_fields = ('views',)
    ordering = ('-created_date',)

    # O‘rtacha reyting
    def average_rating(self, obj):
        return obj.average_rating

    average_rating.short_description = "O‘rtacha reyting"

    # Yoqtirishlar soni
    def likes_count(self, obj):
        return Like.objects.filter(stadium=obj).count()

    likes_count.short_description = "Yoqtirishlar soni"

    # Istaklar ro‘yxati soni
    def wishlist_count(self, obj):
        return Wishlist.objects.filter(stadium=obj).count()

    wishlist_count.short_description = "Istaklar soni"

    # Bronlar soni
    def bookings_count(self, obj):
        from apps.bookings.models import Booking
        return Booking.objects.filter(stadium=obj).count()

    bookings_count.short_description = "Bronlar soni"

    # Rasmlar soni
    def images_count(self, obj):
        return obj.images.count()

    images_count.short_description = "Rasmlar soni"


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
