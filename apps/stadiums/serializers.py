from rest_framework import serializers
from .models import Stadium, StadiumLocation, StadiumImage, Rating, Like, Wishlist, CommentImage, Comment
from apps.account.models import User
from ..account.serializers import UserSerializer, UserProfileSerializer


# ------------------- StadiumLocation Serializers -------------------

class StadiumLocationPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = StadiumLocation
        fields = ['address', 'latitude', 'longitude']


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
    location = StadiumLocationPostSerializer()
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = Stadium
        fields = ['name', 'price', 'description', 'owner', 'manager', 'location', 'images']

    def create(self, validated_data):
        location_data = validated_data.pop('location')
        image_files = validated_data.pop('images', [])

        stadium = Stadium.objects.create(**validated_data)
        StadiumLocation.objects.create(stadium=stadium, **location_data)

        for image in image_files:
            StadiumImage.objects.create(stadium=stadium, image=image)

        return stadium

    def update(self, instance, validated_data):
        location_data = validated_data.pop('location', None)
        image_files = validated_data.pop('images', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if location_data:
            location, _ = StadiumLocation.objects.get_or_create(stadium=instance)
            for attr, value in location_data.items():
                setattr(location, attr, value)
            location.save()

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

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user_id'] = user.id
        return super().create(validated_data)

class RankSerializer(serializers.ModelSerializer):
    stadium = StadiumGetSerializer(read_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'stadium', 'rank']

    def create(self, validated_data):
        user = self.context['request'].user
        sid = self.context['sid']
        validated_data['user_id'] = user.id
        validated_data['stadium_id'] = sid
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
        fields = ['id', 'parent', 'user', 'comment', 'images',  'created_date']


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