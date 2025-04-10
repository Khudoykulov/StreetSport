from django.contrib import admin
from .models import Booking

# Bron qilish admin
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    # Ro'yxatda ko'rinadigan ustunlar
    list_display = (
        'id',
        'stadium',
        'user',
        'booking_date',
        'start_time_display',
        'end_time_display',
        'duration',
        'is_active',
        'created_date'
    )

    # Filtrlash uchun maydonlar
    list_filter = (
        'booking_date',
        'start_hour',
        'duration',
        'is_active',
        'stadium',
    )

    # Qidiruv uchun maydonlar
    search_fields = (
        'stadium__name',  # Stadion nomida qidirish
        'user__username',  # Foydalanuvchi nomida qidirish
        'booking_date',  # Sana bo'yicha qidirish
    )

    # Tartiblash
    ordering = ('-booking_date', '-start_hour')

    # Sahifada har bir yozuv uchun 20 ta element ko'rsatish
    list_per_page = 20

    # Faqat o'qish uchun maydonlar
    readonly_fields = ('created_date',)

    # Admin paneldagi shaklda ko'rinadigan maydonlar tartibi
    fieldsets = (
        (None, {
            'fields': ('stadium', 'user', 'booking_date', 'start_hour', 'duration')
        }),
        ('Qo‘shimcha ma’lumotlar', {
            'fields': ('is_active', 'created_date'),
            'classes': ('collapse',)  # Bu qismni yig'ib qo'yish mumkin
        }),
    )

    # Vaqtni chiroyli ko'rsatish uchun maxsus metodlar
    def start_time_display(self, obj):
        """Boshlanish vaqtini 14:00 shaklida ko'rsatadi"""
        return f"{obj.start_hour:02d}:00"

    start_time_display.short_description = "Boshlanish vaqti"  # Ustun nomi

    def end_time_display(self, obj):
        """Tugash vaqtini 16:00 shaklida ko'rsatadi"""
        end_hour = obj.start_hour + obj.duration
        return f"{end_hour:02d}:00"

    end_time_display.short_description = "Tugash vaqti"  # Ustun nomi

    # Bronni faolsizlantirish uchun maxsus harakat
    actions = ['deactivate_bookings']

    def deactivate_bookings(self, request, queryset):
        """Tanlangan bronlarni faolsizlantirish"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} ta bron faolsizlantirildi.")

    deactivate_bookings.short_description = "Tanlangan bronlarni faolsizlantirish"

    # Yangi bron qo'shishda foydalanuvchini avto-to'ldirish
    def save_model(self, request, obj, form, change):
        if not change:  # Agar yangi ob'ekt bo'lsa
            if not obj.user:
                obj.user = request.user  # Joriy adminni foydalanuvchi sifatida qo‘shish
        super().save_model(request, obj, form, change)
