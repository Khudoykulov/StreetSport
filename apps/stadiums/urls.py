from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import StadiumViewSet, RatingViewSet, LikeViewSet, WishlistViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'stadiums', StadiumViewSet, basename='stadium'),
router.register('wishlists', WishlistViewSet)
router.register('likes', LikeViewSet)
# router.register('(?P<sid>[0-9]+)/ranks', RatingViewSet)
# router.register('(?P<sid>[0-9]+)/comments', CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('stadiums/<int:sid>/ranks/', RatingViewSet.as_view({'get': 'list', 'post': 'create'}), name='rating-list'),
    path('stadiums/<int:sid>/ranks/<int:pk>/',
         RatingViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='rating-detail'),
]
