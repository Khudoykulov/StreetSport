from rest_framework.permissions import BasePermission
from rest_framework import permissions


class IsAdminUser(BasePermission):
    """
    Faqat admin foydalanuvchilarga barcha huquqlarni beradi:
    - Qo'shish (POST)
    - O'qish (GET)
    - Yangilash (PUT/PATCH)
    - O'chirish (DELETE)
    Boshqa rollarga hech qanday ruxsat berilmaydi.
    """

    def has_permission(self, request, view):
        # Foydalanuvchi autentifikatsiya qilingan va admin ekanligini tekshirish
        return request.user.is_authenticated and request.user.role == 'admin'

    def has_object_permission(self, request, view, obj):
        # Muayyan ob'ekt ustida faqat admin ishlay oladi
        return request.user.is_authenticated and request.user.role == 'admin'


class IsAdminOrOwner(BasePermission):
    """
    - Admin: Barcha managerlar ustida to‘liq huquqqa ega.
    - Owner: Faqat o‘zi qo‘shgan managerlar ustida to‘liq huquqqa ega.
    """

    def has_permission(self, request, view):
        # Foydalanuvchi autentifikatsiya qilinganligini tekshirish
        if not request.user.is_authenticated:
            return False

        # Admin yoki Owner bo‘lsa, umumiy ruxsat beriladi (qo‘shish va ro‘yxatni ko‘rish uchun)
        return request.user.role in ('admin', 'owner')

    def has_object_permission(self, request, view, obj):
        # Foydalanuvchi autentifikatsiya qilinganligini tekshirish
        if not request.user.is_authenticated:
            return False

        # Admin bo‘lsa, har qanday manager ustida ishlay oladi
        if request.user.role == 'admin':
            return True

        # Owner bo‘lsa, faqat o‘zi qo‘shgan managerlar ustida ishlay oladi
        if request.user.role == 'owner':
            return obj.created_by == request.user

        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_superuser


class IsReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.id == request.user.id


class CustomBookingPermission(BasePermission):
    """
    Maxsus ruxsat sinfi:
    - GET: Hamma uchun ochiq
    - CREATE: Faqat oddiy user (is_staff=False, is_superuser=False)
    - DELETE/PUT/PATCH: Faqat 'Manager' guruhi
    """

    def has_permission(self, request, view):
        # GET va boshqa xavfsiz metodlar uchun hamma uchun ruxsat
        if request.method in permissions.SAFE_METHODS:
            return True

        # Autentifikatsiya qilinmagan foydalanuvchilar uchun ruxsat yo‘q
        if not request.user.is_authenticated:
            return False

        # CREATE uchun: Faqat oddiy user
        if view.action == 'create':
            return not request.user.is_staff and not request.user.is_superuser

        # DELETE, PUT, PATCH uchun: Faqat 'Manager' guruhi
        if view.action in ['destroy', 'update', 'partial_update']:
            return request.user.groups.filter(name='Manager').exists()

        return False

    def has_object_permission(self, request, view, obj):
        # GET va boshqa xavfsiz metodlar uchun hamma uchun ruxsat
        if request.method in permissions.SAFE_METHODS:
            return True

        # DELETE, PUT, PATCH uchun: Faqat 'Manager' guruhi
        if view.action in ['destroy', 'update', 'partial_update']:
            return request.user.groups.filter(name='Manager').exists()

        return False


class IsAuthor(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.user


class IsAdminOrSelf(BasePermission):
    """
    Admin hamma narsani qila oladi.
    Foydalanuvchi faqat o‘z profilini ko‘ra oladi va o‘zgartira oladi.
    """

    def has_permission(self, request, view):
        # Foydalanuvchi autentifikatsiya qilinganligini tekshirish
        if not request.user.is_authenticated:
            return False

        # Admin bo‘lsa, hamma narsaga ruxsat
        if request.user.role == 'admin':
            return True

        # Agar foydalanuvchi oddiy user bo‘lsa, faqat o‘zini ko‘rish/o‘zgartirish uchun ruxsat
        return True  # Bu yerda umumiy ruxsat beriladi, lekin ob'ekt tekshiruvi has_object_permission da amalga oshiriladi

    def has_object_permission(self, request, view, obj):
        # Foydalanuvchi autentifikatsiya qilinganligini tekshirish
        if not request.user.is_authenticated:
            return False

        # Admin bo‘lsa, har qanday profil ustida ishlay oladi
        if request.user.role == 'admin':
            return True

        # Foydalanuvchi faqat o‘z profiliga kirishi mumkin
        return obj == request.user


class IsAdminOrOwnerStadium(BasePermission):
    """
    Ruxsatlar:
    - Barcha foydalanuvchilar (shu jumladan anonimlar) READ (GET) qila oladi
    - admin hamma narsani qila oladi
    - owner o‘ziga tegishli stadiumni tahrirlash/o‘chirish mumkin
    - manager faqat o‘ziga tegishli stadiumni ko‘rishi mumkin (o‘zgartira olmaydi)
    - oddiy user faqat ko‘rishi mumkin
    """

    def has_permission(self, request, view):
        # Barcha foydalanuvchilarga ko‘rishga ruxsat beriladi
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        return request.user.role in ['admin', 'owner']

    def has_object_permission(self, request, view, obj):
        # Barcha foydalanuvchilarga o‘ziga tegishli bo‘lsa ko‘rishga ruxsat beriladi
        if request.method in permissions.SAFE_METHODS:
            return (
                    request.user.role == 'admin' or
                    obj.owner == request.user or
                    obj.manager == request.user
            )

        if not request.user.is_authenticated:
            return False

        if request.user.role == 'admin':
            return True

        if request.user.role == 'owner':
            return obj.owner == request.user

        return False