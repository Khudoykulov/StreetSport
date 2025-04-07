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
            'id', 'name', 'phone', 'is_active', 'is_superuser', 'is_staff', 'role', 'modified_date', 'created_date')


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
        user.role = 'owner'
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
        valid_roles = [choice[1] for choice in User.ROLE_CHOICES]
        if value not in valid_roles:
            raise serializers.ValidationError("Noto‘g‘ri role kiritildi.")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, validators=[validate_password])

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if self.context['request'].user.check_password(password):
            raise ValidationError('Current must not equal to new password')
        if password == password2:
            return attrs
        raise ValidationError('Passwords do not match')

    def create(self, validated_data):
        password = validated_data.get('password')
        user = self.context['request'].user
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
