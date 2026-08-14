from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.walkthroughs.views import walkthrough_detail_page
from apps.journal.views import note_detail_page


@api_view(['GET'])
def api_root(request):
    return Response({
        'status': 'online',
        'version': 'v1',
        'endpoints': {
            'skills': '/api/skills/',
            'skills_by_category': '/api/skills/by_category/',
            'projects': '/api/projects/',
            'walkthroughs': '/api/walkthroughs/',
            'labs': '/api/labs/',
            'journal': '/api/journal/',
            'roadmap': '/api/roadmap/',
            'roadmap_by_horizon': '/api/roadmap/by_horizon/',
        }
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    # Pages détail server-rendues — URLs propres et partageables,
    # rendues accessibles sur le domaine principal via un rewrite Vercel.
    path('walkthroughs/<slug:slug>/', walkthrough_detail_page, name='walkthrough-detail-page'),
    path('notes/<slug:slug>/', note_detail_page, name='note-detail-page'),
    path('api/', api_root),
    path('api/', include('apps.skills.urls')),
    path('api/', include('apps.projects.urls')),
    path('api/', include('apps.walkthroughs.urls')),
    path('api/', include('apps.labs.urls')),
    path('api/', include('apps.journal.urls')),
    path('api/', include('apps.roadmap.urls')),
    path('api-auth/', include('rest_framework.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
