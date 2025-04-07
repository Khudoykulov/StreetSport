from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from apps.account.permissions import IsAdminOrOwner, IsAuthor, IsAdminOrReadOnly
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
    permission_classes = [IsAdminOrOwner]
    parser_classes = (MultiPartParser, FormParser)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return StadiumGetSerializer
        return StadiumPostSerializer


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
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['stadium__name']

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Rating.objects.all()
        return Rating.objects.none()

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['sid'] = self.kwargs.get('sid')
        return ctx


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
