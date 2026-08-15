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
            'stack': '/api/stack/',
        }
    })


# Ordre fixe du curriculum (manuel DevOps/DevSecOps de l'utilisateur).
# Ne change jamais tout seul — c'est une référence stable, pas une donnée
# à éditer. Le statut de chaque techno se déduit automatiquement des tags
# utilisés dans les walkthroughs/notes publiés, zéro entretien manuel.
STACK_CURRICULUM = [
    ('linux', 'linux.service'),
    ('git', 'git.service'),
    ('docker', 'docker.service'),
    ('kubernetes', 'kubernetes.service'),
    ('terraform', 'terraform.service'),
    ('ansible', 'ansible.service'),
    ('ci/cd', 'cicd.service'),
    ('monitoring', 'monitoring.service'),
    ('devsecops', 'devsecops.service'),
    ('cloud', 'cloud.service'),
    ('cybersécurité', 'security.service'),
]
QUEUED_LIMIT = 3
ACTIVE_LIMIT = 6
LEARNING_LIMIT = 3


@api_view(['GET'])
def stack_status(request):
    from apps.walkthroughs.models import Walkthrough
    from apps.journal.models import JournalEntry

    def tags_for(qs):
        tags = []
        for item in qs:
            tags += [t.lower() for t in (item.tags or [])]
        return tags

    wt_tags = tags_for(Walkthrough.objects.filter(status='published'))
    note_tags = tags_for(JournalEntry.objects.filter(published=True))

    active, learning, queued = [], [], []
    for key, service in STACK_CURRICULUM:
        wt_count = wt_tags.count(key)
        note_count = note_tags.count(key)
        if wt_count > 0:
            active.append({'service': service, 'label': key, 'status': 'active (mastered)', 'count': wt_count, 'unit': 'walkthrough'})
        elif note_count > 0:
            learning.append({'service': service, 'label': key, 'status': 'activating (learning)', 'count': note_count, 'unit': 'note'})
        else:
            queued.append({'service': service, 'label': key, 'status': 'inactive (queued)', 'count': 0})

    active.sort(key=lambda x: -x['count'])
    learning.sort(key=lambda x: -x['count'])

    return Response({
        'active': active[:ACTIVE_LIMIT],
        'learning': learning[:LEARNING_LIMIT],
        'queued': queued[:QUEUED_LIMIT],
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    # Pages détail server-rendues — URLs propres et partageables,
    # rendues accessibles sur le domaine principal via un rewrite Vercel.
    path('walkthroughs/<slug:slug>/', walkthrough_detail_page, name='walkthrough-detail-page'),
    path('notes/<slug:slug>/', note_detail_page, name='note-detail-page'),
    path('api/', api_root),
    path('api/stack/', stack_status),
    path('api/', include('apps.skills.urls')),
    path('api/', include('apps.projects.urls')),
    path('api/', include('apps.walkthroughs.urls')),
    path('api/', include('apps.labs.urls')),
    path('api/', include('apps.journal.urls')),
    path('api/', include('apps.roadmap.urls')),
    path('api-auth/', include('rest_framework.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
