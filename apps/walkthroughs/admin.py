from django.contrib import admin
from .models import Walkthrough

@admin.register(Walkthrough)
class WalkthroughAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'reading_time', 'published_at']
    list_filter = ['status']
    list_editable = ['status']
    search_fields = ['title', 'objective']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Identity', {
            'fields': ('title', 'slug', 'status', 'tags', 'reading_time', 'published_at')
        }),
        ('Structure', {
            'fields': ('objective', 'stack', 'architecture', 'problems_encountered', 'lessons_learned')
        }),
        ('Content Markdown', {
            'fields': ('content', 'obsidian_file'),
            'classes': ('wide',),
        }),
        ('Meta', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
