from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserToken
from .forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    # `created_by` ni list_display ga qo‘shish
    list_display = ('id', 'name', 'phone', 'role', 'is_active', 'created_by', 'created_date')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'created_by')  # `created_by` bo‘yicha filtr qo‘shish
    search_fields = ('name', 'phone', 'created_by__phone', 'created_by__name')  # `created_by` bo‘yicha qidiruv
    ordering = ('-created_date',)

    readonly_fields = ('last_login', 'modified_date', 'created_date', 'created_by')  # `created_by` ni faqat o‘qish uchun qilish

    fieldsets = (
        (None, {
            'fields': ('name', 'phone', 'password', 'role', 'created_by', 'user_permissions')  # `created_by` ni qo‘shish
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'modified_date', 'created_date')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'phone', 'role', 'password1', 'password2'),  # Yangi foydalanuvchi qo‘shishda created_by ko‘rinmaydi
        }),
    )

    def save_model(self, request, obj, form, change):
        # Agar yangi foydalanuvchi qo‘shilayotgan bo‘lsa, created_by ga joriy adminni qo‘shish
        if not change:  # Agar bu yangi ob‘yekt bo‘lsa
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'is_used', 'token', 'created_date')
    date_hierarchy = 'created_date'
    list_filter = ('is_used',)
    search_fields = ('user__username', 'user_full_name', 'token')

admin.site.register(User, UserAdmin)

admin.site.index_title = _('StreetSport administration')
admin.site.site_header = _('StreetSport')