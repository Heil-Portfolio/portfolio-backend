from rest_framework import viewsets
from .models import Lab
from .serializers import LabSerializer
class LabViewSet(viewsets.ModelViewSet):
    queryset = Lab.objects.all()
    serializer_class = LabSerializer
    lookup_field = 'slug'
