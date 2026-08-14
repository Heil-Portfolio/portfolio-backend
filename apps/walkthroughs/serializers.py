import markdown as md
from rest_framework import serializers
from .models import Walkthrough

class WalkthroughListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Walkthrough
        exclude = ['content']

class WalkthroughDetailSerializer(serializers.ModelSerializer):
    content_html = serializers.SerializerMethodField()
    source_note_info = serializers.SerializerMethodField()

    class Meta:
        model = Walkthrough
        fields = '__all__'

    def get_content_html(self, obj):
        if not obj.content:
            return ''
        return md.markdown(
            obj.content,
            extensions=['fenced_code', 'tables', 'nl2br', 'sane_lists']
        )

    def get_source_note_info(self, obj):
        if not obj.source_note or not obj.source_note.published:
            return None
        return {
            'title': obj.source_note.title,
            'slug': obj.source_note.slug,
            'entry_date': obj.source_note.entry_date,
        }
