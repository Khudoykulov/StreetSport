from rest_framework import viewsets
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.account.permissions import IsAdminOrOwner, IsAuthor, IsAdminOrReadOnly, IsAdminOrOwnerStadium, IsAdminUser
from .mixins import CreateViewSetMixin
from .models import Stadium, Rating, Like, Wishlist, CommentImage, Comment
from .serializers import (
    StadiumGetSerializer,
    StadiumPostSerializer,
    WishListSerializer,
    WishListPostSerializer,
    LikeSerializer,
    LikePostSerializer,
    RankSerializer,
    CommentImageSerializer,
    CommentSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import MultiPartParser, FormParser


class StadiumViewSet(viewsets.ModelViewSet):
    queryset = Stadium.objects.all().order_by('-created_date')
    permission_classes = [IsAdminOrOwnerStadium]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        user = self.request.user
        qs = Stadium.objects.all().order_by('-created_date')

        if not user.is_authenticated:
            return Stadium.objects.none()

        if user.role == 'admin':
            return qs
        elif user.role == 'owner':
            return qs.filter(owner=user)
        elif user.role == 'manager':
            return qs.filter(manager=user)
        return Stadium.objects.none()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return StadiumGetSerializer
        return StadiumPostSerializer

    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'price': {'type': 'number'},
                    'description': {'type': 'string'},
                    'owner': {'type': 'integer'},
                    'manager': {'type': 'integer'},
                    'address': {'type': 'string'},
                    'latitude': {'type': 'string'},
                    'longitude': {'type': 'string'},
                    'images': {
                        'type': 'array',
                        'items': {'type': 'string', 'format': 'binary'},  # Fayl yuklash uchun
                    },
                },
                'required': ['name', 'price', 'owner'],  # Faqat modelda majburiy maydonlar
            }
        },
        responses={201: StadiumGetSerializer},  # StadiumGetSerializer ishlatiladi
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'price': {'type': 'number'},
                    'description': {'type': 'string'},
                    'owner': {'type': 'integer'},
                    'manager': {'type': 'integer'},
                    'address': {'type': 'string'},
                    'latitude': {'type': 'string'},
                    'longitude': {'type': 'string'},
                    'images': {
                        'type': 'array',
                        'items': {'type': 'string', 'format': 'binary'},  # Fayl yuklash uchun
                    },
                },
                'required': ['name', 'price', 'owner'],  # Faqat modelda majburiy maydonlar
            }
        },
        responses={200: StadiumGetSerializer},  # StadiumGetSerializer ishlatiladi
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Stadionlar bo‘yicha statistika",
        description="Umumiy stadionlar soni, har bir stadionning owneri va menejeri haqida ma’lumot qaytaradi.",
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'total_stadiums': {'type': 'integer'},
                    'stadiums': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'name': {'type': 'string'},
                                'owner': {
                                    'type': 'object',
                                    'properties': {
                                        'id': {'type': 'integer'},
                                        'username': {'type': 'string'},
                                        'role': {'type': 'string'},
                                    },
                                },
                                'manager': {
                                    'type': 'object',
                                    'properties': {
                                        'id': {'type': 'integer'},
                                        'username': {'type': 'string'},
                                        'role': {'type': 'string'},
                                    },
                                },
                            },
                        },
                    },
                },
            }
        }
    )
    @action(detail=False, methods=['get'], url_path='statistics', permission_classes=[IsAuthenticated,IsAdminUser])
    def statistics(self, request):
        # Umumiy stadionlar sonini hisoblash
        total_stadiums = Stadium.objects.count()

        # Har bir stadionning owneri va menejeri haqida ma’lumot
        stadiums = Stadium.objects.all()
        stadium_data = []
        for stadium in stadiums:
            owner_data = {
                'id': stadium.owner.id,
                'username': stadium.owner.name,
                'role': stadium.owner.role,
            } if stadium.owner else None

            manager_data = {
                'id': stadium.manager.id,
                'username': stadium.manager.name,
                'role': stadium.manager.role,
            } if stadium.manager else None

            stadium_data.append({
                'id': stadium.id,
                'name': stadium.name,
                'owner': owner_data,
                'manager': manager_data,
            })

        return Response({
            'total_stadiums': total_stadiums,
            'stadiums': stadium_data,
        })


class WishlistViewSet(CreateViewSetMixin, viewsets.ModelViewSet):
    model = Wishlist
    queryset = Wishlist.objects.all()
    serializer_class = WishListSerializer
    serializer_post_class = WishListPostSerializer
    permission_classes = [IsAuthor | IsAdminOrReadOnly]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['stadium__name']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs.all()
        return qs.filter(user_id=self.request.user.id)


class LikeViewSet(CreateViewSetMixin, viewsets.ModelViewSet):
    model = Like
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    serializer_post_class = LikePostSerializer
    permission_classes = [IsAuthor | IsAdminOrReadOnly]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['stadium__name']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs.all()
        return qs.filter(user_id=self.request.user.id)


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RankSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['stadium__name']  # Stadion nomi bo‘yicha qidiruv
    filterset_fields = ['stadium', 'user', 'rank']  # Filtrlash uchun maydonlar

    def get_queryset(self):
        # Admin yoki superuser bo‘lsa, barcha baholarni qaytarish
        if self.request.user.is_superuser or self.request.user.role == 'admin':
            return Rating.objects.all()
        # Oddiy foydalanuvchilar faqat o‘z baholarini ko‘radi
        return Rating.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['sid'] = self.kwargs.get('sid')  # URL dan sid ni olish
        return ctx

    @extend_schema(
        summary="Stadionga baho qo‘yish",
        description="Foydalanuvchi ma’lum bir stadionga baho qo‘yadi. Bir foydalanuvchi bir stadionga faqat bir marta baho qo‘yishi mumkin.",
        responses={201: RankSerializer},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Baho o‘zgartirish",
        description="Foydalanuvchi o‘z bahosini o‘zgartiradi.",
        responses={200: RankSerializer},
    )
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({"detail": "Siz faqat o‘zingizning bahoingizni o‘zgartira olasiz."}, status=403)
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Baho o‘chirish",
        description="Foydalanuvchi o‘z bahosini o‘chiradi.",
        responses={204: None},
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({"detail": "Siz faqat o‘zingizning bahoingizni o‘chira olasiz."}, status=403)
        return super().destroy(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.filter(parent__isnull=True)
    serializer_class = CommentSerializer
    permission_classes = [IsAuthor]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['sid'] = self.kwargs.get('sid')
        return ctx

    def update(self, request, *args, **kwargs):
        pass

    def get_object(self):
        queryset = self.queryset
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj
