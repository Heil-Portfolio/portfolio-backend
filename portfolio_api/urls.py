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


# Curriculum à deux niveaux : chaque sujet a une liste de synonymes (tags
# précis qui comptent comme preuve pour ce sujet). Référence stable, éditée
# rarement — pas une donnée que l'utilisateur touche au quotidien.
STACK_CURRICULUM = [
    {'key': 'linux', 'label': 'Linux', 'synonyms': ['linux']},
    {'key': 'git', 'label': 'Git', 'synonyms': ['git', 'github', 'gitlab']},
    {'key': 'docker', 'label': 'Docker', 'synonyms': ['docker', 'container', 'conteneur']},
    {'key': 'kubernetes', 'label': 'Kubernetes', 'synonyms': ['kubernetes', 'k8s']},
    {'key': 'terraform', 'label': 'Terraform', 'synonyms': ['terraform']},
    {'key': 'ansible', 'label': 'Ansible', 'synonyms': ['ansible']},
    {'key': 'cicd', 'label': 'CI/CD', 'synonyms': ['ci/cd', 'cicd', 'ci-cd', 'github actions', 'gitlab ci']},
    {'key': 'monitoring', 'label': 'Monitoring', 'synonyms': ['monitoring', 'observabilité', 'observability']},
    {'key': 'devsecops', 'label': 'DevSecOps', 'synonyms': ['devsecops', 'sécurité', 'security', 'firewall', 'crowdsec', 'fail2ban']},
    {'key': 'cloud', 'label': 'Cloud', 'synonyms': ['cloud', 'aws', 'gcp', 'azure', 'ec2', 's3']},
    {'key': 'cybersecurite', 'label': 'Cybersécurité', 'synonyms': ['cybersécurité', 'cybersecurity']},
    {'key': 'architecture', 'label': 'Architecture & Systèmes distribués', 'synonyms': [
        'architecture', 'microservices', 'service-discovery', 'messaging',
        'eureka', 'rabbitmq', 'kafka', 'distributed-systems',
    ]},
]
QUEUED_LIMIT = 3
ACTIVE_LIMIT = 6
LEARNING_LIMIT = 3
MASTERED_THRESHOLD = 5  # walkthroughs requis sur un sujet avant de le dire "mastered"


@api_view(['GET'])
def curriculum_order(request):
    """Ordre + synonymes du curriculum, exposé pour que le frontend groupe
    et sous-groupe les walkthroughs/notes sans dupliquer la liste."""
    return Response(STACK_CURRICULUM)


@api_view(['GET'])
def stack_status(request):
    from apps.walkthroughs.models import Walkthrough
    from apps.journal.models import JournalEntry

    walkthroughs = list(Walkthrough.objects.filter(status='published'))
    notes = list(JournalEntry.objects.filter(published=True))

    def matches(item, synonyms):
        tags = [t.lower() for t in (item.tags or [])]
        return any(s in tags for s in synonyms)

    active, learning, queued = [], [], []
    for topic in STACK_CURRICULUM:
        synonyms = topic['synonyms']
        # Un item ne compte qu'une fois, même s'il porte plusieurs synonymes
        # du même sujet (évite le gonflement par tag-stuffing).
        wt_count = sum(1 for w in walkthroughs if matches(w, synonyms))
        note_count = sum(1 for n in notes if matches(n, synonyms))
        service = f"{topic['key']}.service"
        if wt_count >= MASTERED_THRESHOLD:
            active.append({'service': service, 'label': topic['label'], 'status': 'active (mastered)', 'count': wt_count, 'unit': 'walkthrough'})
        elif wt_count > 0:
            learning.append({'service': service, 'label': topic['label'], 'status': 'activating (learning)', 'count': wt_count, 'unit': 'walkthrough'})
        elif note_count > 0:
            learning.append({'service': service, 'label': topic['label'], 'status': 'activating (learning)', 'count': note_count, 'unit': 'note'})
        else:
            queued.append({'service': service, 'label': topic['label'], 'status': 'inactive (queued)', 'count': 0})

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
    path('api/curriculum/', curriculum_order),
    path('api/', include('apps.skills.urls')),
    path('api/', include('apps.projects.urls')),
    path('api/', include('apps.walkthroughs.urls')),
    path('api/', include('apps.labs.urls')),
    path('api/', include('apps.journal.urls')),
    path('api/', include('apps.roadmap.urls')),
    path('api-auth/', include('rest_framework.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
