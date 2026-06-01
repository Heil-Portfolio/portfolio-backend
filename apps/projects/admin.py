from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'status', 'order']
    list_filter = ['status']
    list_editable = ['status', 'order']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
