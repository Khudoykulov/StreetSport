from rest_framework import serializers
from .models import Stadium, StadiumLocation, StadiumImage, Rating, Like, Wishlist, CommentImage, Comment
from apps.account.models import User
from ..account.serializers import UserSerializer, UserProfileSerializer


# ------------------- StadiumLocation Serializers -------------------

class StadiumLocationPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = StadiumLocation
        fields = ['address', 'latitude', 'longitude']

    def validate(self, attrs):
        # Agar address bo‘sh bo‘lsa, xatolik qaytarish
        if not attrs.get('address'):
            raise serializers.ValidationError("Manzil (address) kiritilishi shart.")
        return attrs


class StadiumLocationGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = StadiumLocation
        fields = ['id', 'address', 'latitude', 'longitude']


# ------------------- StadiumImage Serializer -------------------

class StadiumImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StadiumImage
        fields = ['id', 'image']


# ------------------- Stadium Serializers -------------------

class StadiumPostSerializer(serializers.ModelSerializer):
    # `location` o‘rniga alohida maydonlar qo‘shiladi
    address = serializers.CharField(write_only=True, required=False)
    latitude = serializers.CharField(write_only=True, required=False, allow_blank=True)
    longitude = serializers.CharField(write_only=True, required=False, allow_blank=True)

    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = Stadium
        fields = ['name', 'price', 'description', 'owner', 'manager', 'address', 'latitude', 'longitude', 'images']

    def validate(self, attrs):
        # Majburiy maydonlarni tekshirish
        if not attrs.get('name'):
            raise serializers.ValidationError({"name": "This field is required."})
        if not attrs.get('price'):
            raise serializers.ValidationError({"price": "This field is required."})
        if not attrs.get('owner'):
            raise serializers.ValidationError({"owner": "This field is required."})
        owner = attrs.get('owner')
        if owner:
            try:
                owner_user = User.objects.get(id=owner.id)
                if owner_user.role not in ['owner', 'admin']:
                    raise serializers.ValidationError(
                        {"owner": "Owner faqat 'owner' yoki 'admin' rolidagi foydalanuvchi bo‘lishi kerak."})
            except User.DoesNotExist:
                raise serializers.ValidationError({"owner": "Bunday ID ga ega foydalanuvchi topilmadi."})
        # Manager uchun role tekshiruvi (manager ixtiyoriy bo‘lgani uchun faqat mavjud bo‘lsa tekshiramiz)
        manager = attrs.get('manager')
        if manager:
            try:
                manager_user = User.objects.get(id=manager.id)
                if manager_user.role != 'manager':
                    raise serializers.ValidationError(
                        {"manager": "Manager faqat 'manager' rolidagi foydalanuvchi bo‘lishi kerak."})
            except User.DoesNotExist:
                raise serializers.ValidationError({"manager": "Bunday ID ga ega foydalanuvchi topilmadi."})

        return attrs

    def create(self, validated_data):
        # `location` maydonlarini olish
        address = validated_data.pop('address', "")
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)
        image_files = validated_data.pop('images', [])

        # Stadium ob‘ektini yaratish
        stadium = Stadium.objects.create(**validated_data)

        # StadiumLocation ob‘ektini yaratish
        StadiumLocation.objects.create(
            stadium=stadium,
            address=address,
            latitude=latitude,
            longitude=longitude
        )

        # Agar rasm fayllari berilgan bo‘lsa, ularni saqlash
        for image in image_files:
            StadiumImage.objects.create(stadium=stadium, image=image)

        return stadium

    def update(self, instance, validated_data):
        address = validated_data.pop('address', None)
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)
        image_files = validated_data.pop('images', None)

        # Stadium atributlarini yangilash
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Agar location maydonlari berilgan bo‘lsa, uni yangilash
        if address is not None or latitude is not None or longitude is not None:
            location, _ = StadiumLocation.objects.get_or_create(stadium=instance)
            if address is not None:
                location.address = address
            if latitude is not None:
                location.latitude = latitude
            if longitude is not None:
                location.longitude = longitude
            location.save()

        # Agar image_files berilgan bo‘lsa, eski rasmlarni o‘chirib, yangilarini qo‘shish
        if image_files is not None:
            instance.images.all().delete()
            for image in image_files:
                StadiumImage.objects.create(stadium=instance, image=image)

        return instance


class StadiumGetSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    manager = UserSerializer(read_only=True)
    location = StadiumLocationGetSerializer(read_only=True)
    images = StadiumImageSerializer(many=True, read_only=True)
    average_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Stadium
        fields = [
            'id', 'name', 'price', 'description',
            'owner', 'manager',
            'views', 'created_date', 'modified_date',
            'location', 'images', 'average_rating'
        ]
        read_only_fields = fields


class WishListSerializer(serializers.ModelSerializer):
    stadium = StadiumGetSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'stadium', 'user']


class WishListPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['id', 'stadium']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user_id'] = user.id
        return super().create(validated_data)


class LikeSerializer(serializers.ModelSerializer):
    stadium = StadiumGetSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'stadium', 'user']


class LikePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'stadium']

    def validate(self, attrs):
        request = self.context['request']
        user = request.user
        stadium = attrs.get('stadium')

        # Foydalanuvchi allaqachon ushbu stadionga like qo‘ygan bo‘lsa, xato qaytaramiz
        if Like.objects.filter(user=user, stadium=stadium).exists():
            raise serializers.ValidationError({"stadium": "Siz allaqachon ushbu stadionga like qo‘ygansiz."})

        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user_id'] = user.id
        return super().create(validated_data)


class RankSerializer(serializers.ModelSerializer):
    stadium = StadiumGetSerializer(read_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'stadium', 'rank', 'user']
        read_only_fields = ['user', 'stadium']  # user va stadium faqat o‘qish uchun

    def validate(self, attrs):
        request = self.context['request']
        user = request.user
        sid = self.context.get('sid')

        # sid ni tekshirish va Stadium ob‘ektini olish
        if not sid:
            raise serializers.ValidationError({"stadium": "Stadion ID si kiritilishi kerak."})
        try:
            stadium = Stadium.objects.get(id=sid)
        except Stadium.DoesNotExist:
            raise serializers.ValidationError({"stadium": "Bunday stadion topilmadi."})

        # Foydalanuvchi allaqachon ushbu stadionga baho qo‘ygan bo‘lsa, xato qaytaramiz
        if Rating.objects.filter(user=user, stadium=stadium).exists():
            raise serializers.ValidationError({"stadium": "Siz allaqachon ushbu stadionga baho qo‘ygansiz."})

        # Rank 1 dan 10 gacha bo‘lishini qo‘shimcha tekshirish
        rank = attrs.get('rank')
        if rank < 1 or rank > 10:
            raise serializers.ValidationError({"rank": "Baho 1 dan 10 gacha bo‘lishi kerak."})

        # Stadium ni validated_data ga qo‘shish
        attrs['stadium'] = stadium
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user  # user ob‘ektini o‘rnatamiz
        return super().create(validated_data)


class CommentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentImage
        fields = ['id', 'image']

    def create(self, validated_data):
        validated_data['comment_id'] = self.context['cid']
        return super().create(validated_data)


class MiniCommentSerializer(serializers.ModelSerializer):
    images = CommentImageSerializer(many=True)

    class Meta:
        model = Comment
        fields = ['id', 'parent', 'user', 'comment', 'images', 'created_date']


class CommentSerializer(serializers.ModelSerializer):
    images = CommentImageSerializer(many=True)
    user = UserProfileSerializer(read_only=True)
    tree = serializers.SerializerMethodField(read_only=True)

    def get_tree(self, obj):
        if obj.parent is None:
            return MiniCommentSerializer(obj.tree.exclude(id=obj.id), many=True).data
        return []

    class Meta:
        model = Comment
        fields = ['id', 'parent', 'user', 'comment', 'images', 'top_level_comment_id', 'tree', 'created_date']
        read_only_fields = ['tree']

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        validated_data['user_id'] = self.context['request'].user.id
        validated_data['stadium_id'] = self.context['sid']
        obj = super().create(validated_data)
        for image in images:
            CommentImage.objects.create(comment=obj, image=image['image'])
        return obj
