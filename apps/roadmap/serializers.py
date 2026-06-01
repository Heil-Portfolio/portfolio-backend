from rest_framework import serializers
from .models import RoadmapItem
class RoadmapItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoadmapItem
        fields = '__all__'
