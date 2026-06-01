from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Skill
from .serializers import SkillSerializer

class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        return Response({
            'current': SkillSerializer(Skill.objects.filter(category='current'), many=True).data,
            'learning': SkillSerializer(Skill.objects.filter(category='learning'), many=True).data,
            'future': SkillSerializer(Skill.objects.filter(category='future'), many=True).data,
        })
