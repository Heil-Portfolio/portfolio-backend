from django.conf import settings
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from .models import JournalEntry
from .serializers import JournalEntrySerializer

class JournalEntryViewSet(viewsets.ModelViewSet):
    queryset = JournalEntry.objects.filter(published=True)
    serializer_class = JournalEntrySerializer
    lookup_field = 'slug'


def note_detail_page(request, slug):
    """Page HTML server-rendue — SEO et aperçus de partage corrects."""
    qs = JournalEntry.objects.all() if request.user.is_staff else JournalEntry.objects.filter(published=True)
    note = get_object_or_404(qs, slug=slug)
    data = JournalEntrySerializer(note).data

    published = JournalEntry.objects.filter(published=True).order_by('-entry_date')
    ids = list(published.values_list('slug', flat=True))
    idx = ids.index(note.slug) if note.slug in ids else -1
    prev_note = published[idx + 1] if 0 <= idx < len(ids) - 1 else None
    next_note = published[idx - 1] if idx > 0 else None

    became = note.became_walkthroughs.filter(status='published').first()

    return render(request, 'journal/detail.html', {
        'note': data,
        'became_walkthrough': became,
        'prev_note': prev_note,
        'next_note': next_note,
        'site_url': settings.SITE_URL,
        'pipeline_stage': 'log',
    })
