from rest_framework import viewsets
from apps.account.permissions import IsAdminOrOwner
from .models import Stadium
from .serializers import StadiumGetSerializer, StadiumPostSerializer

class StadiumViewSet(viewsets.ModelViewSet):
    queryset = Stadium.objects.all().order_by('-created_date')
    permission_classes = [IsAdminOrOwner]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return StadiumGetSerializer
        return StadiumPostSerializer
