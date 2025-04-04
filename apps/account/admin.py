from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserToken
from .forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('id', 'name', 'phone', 'role', 'is_active', 'created_date')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('name', 'phone')
    ordering = ('-created_date',)

    readonly_fields = ('last_login', 'modified_date', 'created_date')

    fieldsets = (
        (None, {
            'fields': ('name', 'phone', 'password', 'role', 'user_permissions')
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
            'fields': ('name', 'phone', 'role', 'password1', 'password2'),
        }),
    )

@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'is_used', 'token', 'created_date')
    date_hierarchy = 'created_date'
    list_filter = ('is_used',)
    search_fields = ('user__username', 'user_full_name', 'token')


admin.site.register(User, UserAdmin)

admin.site.index_title = _('StreetSport administration')
admin.site.site_header = _('StreetSport')