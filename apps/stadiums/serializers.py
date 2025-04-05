from rest_framework import serializers
from .models import Stadium, StadiumLocation, StadiumImage
from apps.account.models import User
from ..account.serializers import UserSerializer


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
