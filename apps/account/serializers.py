from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User, UserToken
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserRegisterSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(
        max_length=11, required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password1 = serializers.CharField(write_only=True, validators=[validate_password],
                                      help_text='Password must meet criteria.')
    password2 = serializers.CharField(write_only=True)

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Telefon raqami allaqachon ishlatilgan.")
        return value

    def validate(self, attrs):
        password1 = attrs.get('password1')
        password2 = attrs.get('password2')

        if password1 != password2:
            raise ValidationError('Parollar mos kelmaydi.')
        return attrs

    class Meta:
        model = User
        fields = ['name', 'phone', 'password1', 'password2']
        extra_kwargs = {
            'name': {'required': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            name=validated_data['name'],
            phone=validated_data['phone'],
            password=validated_data['password1']
        )
        user.is_active = True
        user.role = 'user'  # Default role beriladi
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['phone'] = user.phone
        token['role'] = user.role  # Add role to the token
        token['created_date'] = user.created_date.strftime('%d.%m.%Y %H:%M:%S')
        return token


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'name', 'phone', 'modified_date', 'created_date')


class SuperUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('phone', 'name', 'password')

    def create(self, validated_data):
        validated_data['is_superuser'] = True
        validated_data['is_staff'] = True
        validated_data['is_active'] = True
        user = User.objects.create_superuser(**validated_data)
        user.role = 'admin'  # Super user role
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone', ]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'phone']


# serializers.py
class OwnerCreateSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['name', 'phone', 'password1', 'password2']

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Parollar mos emas")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password1')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.save()
        return user


class OwnerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'role', 'created_date']


class ManagerCreateSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['name', 'phone', 'password1', 'password2']

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Parollar mos emas")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password1')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.role = 'manager'
        user.is_active = True
        user.save()
        return user

class ManagerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'role', 'created_date']


class UserRoleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['role']

    def validate_role(self, value):
        # Faqat 'owner' roliga ruxsat berish
        if value != 'owner':
            raise serializers.ValidationError("Rol faqat 'owner' ga o‘zgartirilishi mumkin.")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=False)  # Admin uchun ixtiyoriy
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, validators=[validate_password])

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        request = self.context['request']
        user = request.user

        # Agar user_id berilgan bo‘lsa, uni olish
        user_id = attrs.get('user_id')
        if user_id:
            if not user.role == 'admin':
                raise ValidationError("Faqat admin boshqa foydalanuvchilarning parolini o‘zgartira oladi.")
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise ValidationError("Bunday ID ga ega foydalanuvchi topilmadi.")

        # Joriy parol yangi parolga teng bo‘lmasligini tekshirish
        if user.check_password(password):
            raise ValidationError("Joriy parol yangi parolga teng bo‘lmasligi kerak.")

        # Parollar mosligini tekshirish
        if password != password2:
            raise ValidationError("Parollar mos emas.")

        return attrs

    def save(self):
        validated_data = self.validated_data
        password = validated_data.get('password')
        request = self.context['request']
        user = request.user

        # Agar user_id berilgan bo‘lsa, admin o‘sha foydalanuvchini yangilaydi
        if 'user_id' in validated_data and validated_data['user_id']:
            user = User.objects.get(id=validated_data['user_id'])

        user.set_password(password)
        user.save()
        return user

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, validators=[validate_password])
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, validators=[validate_password])

    def validate(self, attrs):
        old_password = attrs.get('old_password')
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if self.context['request'].user.check_password(old_password):
            if old_password == password:
                raise ValidationError('Current must not equal to new password')
            if password == password2:
                return attrs
            raise ValidationError("Passwords do not match")
        raise ValidationError('Old password does not match')

    def create(self, validated_data):
        password = validated_data.get('password')
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user


class UserListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    def get_created_by_name(self, obj):
        return obj.created_by.name if obj.created_by else "None"

    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'role', 'is_active', 'created_date', 'created_by_name']