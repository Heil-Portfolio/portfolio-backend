import markdown as md
from rest_framework import serializers
from .models import JournalEntry

class JournalEntrySerializer(serializers.ModelSerializer):
    content_html = serializers.SerializerMethodField()
    became_walkthrough = serializers.SerializerMethodField()

    class Meta:
        model = JournalEntry
        fields = '__all__'

    def get_content_html(self, obj):
        if not obj.content:
            return ''
        return md.markdown(
            obj.content,
            extensions=['fenced_code', 'tables', 'nl2br', 'sane_lists']
        )

    def get_became_walkthrough(self, obj):
        w = obj.became_walkthroughs.filter(status='published').first()
        if not w:
            return None
        return {'title': w.title, 'slug': w.slug}
