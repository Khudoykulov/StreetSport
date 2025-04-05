from django.contrib import admin
from .models import Stadium, StadiumLocation, StadiumImage

# Stadion rasmlarini inline tarzda ko‘rsatish uchun
class StadiumImageInline(admin.TabularInline):
    model = StadiumImage
    extra = 1
    fields = ('image',)
    readonly_fields = ('image',)

# Stadion joylashuvini inline tarzda ko‘rsatish uchun
class StadiumLocationInline(admin.StackedInline):
    model = StadiumLocation
    extra = 0
    fields = ('address', 'latitude', 'longitude')

# Stadion admin
@admin.register(Stadium)
class StadiumAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'owner', 'manager', 'views', 'created_date', 'average_rating')
    list_filter = ('owner', 'manager', 'created_date')
    search_fields = ('name', 'description')
    inlines = [StadiumLocationInline, StadiumImageInline]
    list_editable = ('price',)
    ordering = ('-created_date',)

    def average_rating(self, obj):
        return obj.average_rating
    average_rating.short_description = "O‘rtacha reyting"

# Agar alohida ro‘yxatdan o‘tkazmoqchi bo‘lsangiz (ixtiyoriy)
@admin.register(StadiumLocation)
class StadiumLocationAdmin(admin.ModelAdmin):
    list_display = ('stadium', 'address', 'latitude', 'longitude')
    search_fields = ('stadium__name', 'address')

@admin.register(StadiumImage)
class StadiumImageAdmin(admin.ModelAdmin):
    list_display = ('stadium', 'image',)
    search_fields = ('stadium__name',)