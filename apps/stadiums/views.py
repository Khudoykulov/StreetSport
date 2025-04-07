from rest_framework import viewsets
from apps.account.permissions import IsAdminOrOwner
from .models import Stadium
from .serializers import StadiumGetSerializer, StadiumPostSerializer
from rest_framework.parsers import MultiPartParser, FormParser

class StadiumViewSet(viewsets.ModelViewSet):
    queryset = Stadium.objects.all().order_by('-created_date')
    permission_classes = [IsAdminOrOwner]
    parser_classes = (MultiPartParser, FormParser)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return StadiumGetSerializer
        return StadiumPostSerializer
