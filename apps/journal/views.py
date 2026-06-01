from rest_framework import viewsets
from .models import JournalEntry
from .serializers import JournalEntrySerializer
class JournalEntryViewSet(viewsets.ModelViewSet):
    queryset = JournalEntry.objects.filter(published=True)
    serializer_class = JournalEntrySerializer
    lookup_field = 'slug'
