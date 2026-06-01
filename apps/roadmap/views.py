from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import RoadmapItem
from .serializers import RoadmapItemSerializer

class RoadmapItemViewSet(viewsets.ModelViewSet):
    queryset = RoadmapItem.objects.all()
    serializer_class = RoadmapItemSerializer

    @action(detail=False, methods=['get'])
    def by_horizon(self, request):
        return Response({
            'short': RoadmapItemSerializer(RoadmapItem.objects.filter(horizon='short'), many=True).data,
            'medium': RoadmapItemSerializer(RoadmapItem.objects.filter(horizon='medium'), many=True).data,
            'long': RoadmapItemSerializer(RoadmapItem.objects.filter(horizon='long'), many=True).data,
        })
