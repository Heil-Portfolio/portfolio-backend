from django.contrib import admin
from .models import JournalEntry
@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['entry_date', 'title', 'published']
    list_filter = ['published']
    list_editable = ['published']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'entry_date'
