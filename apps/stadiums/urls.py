from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .models import Rating
from .views import StadiumViewSet, RatingViewSet, LikeViewSet, WishlistViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'stadiums', StadiumViewSet, basename='stadium'),
router.register('wishlists', WishlistViewSet)
router.register('likes', LikeViewSet)
router.register('(?P<pid>[0-9]+)/ranks', RatingViewSet)
router.register('(?P<pid>[0-9]+)/comments', CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
