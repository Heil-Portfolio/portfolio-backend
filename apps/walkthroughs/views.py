from django.conf import settings
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from .models import Walkthrough
from .serializers import WalkthroughListSerializer, WalkthroughDetailSerializer


def walkthrough_detail_page(request, slug):
    """Page HTML server-rendue — SEO et aperçus de partage corrects."""
    qs = Walkthrough.objects.all()
    if not request.user.is_staff:
        qs = qs.filter(status='published')
    walkthrough = get_object_or_404(qs, slug=slug)
    data = WalkthroughDetailSerializer(walkthrough).data
    return render(request, 'walkthroughs/detail.html', {
        'walkthrough': data,
        'site_url': settings.SITE_URL,
        'pipeline_stage': 'build',
    })

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
