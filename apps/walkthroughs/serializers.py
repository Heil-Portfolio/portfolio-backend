from rest_framework import serializers
from .models import Walkthrough

class WalkthroughListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Walkthrough
        exclude = ['content']

class WalkthroughDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Walkthrough
        fields = '__all__'
