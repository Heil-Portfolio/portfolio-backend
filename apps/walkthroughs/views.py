from rest_framework import viewsets
from .models import Walkthrough
from .serializers import WalkthroughListSerializer, WalkthroughDetailSerializer

class WalkthroughViewSet(viewsets.ModelViewSet):
    queryset = Walkthrough.objects.all()
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return WalkthroughDetailSerializer
        return WalkthroughListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs
