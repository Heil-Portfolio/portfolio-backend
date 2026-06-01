from django.contrib import admin
from .models import RoadmapItem
@admin.register(RoadmapItem)
class RoadmapItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'horizon', 'target_date', 'done', 'order']
    list_filter = ['horizon', 'done']
    list_editable = ['done', 'order']
