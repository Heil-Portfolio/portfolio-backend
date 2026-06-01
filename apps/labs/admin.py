from django.contrib import admin
from .models import Lab
@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    list_display = ['name', 'tag', 'status']
    list_filter = ['status', 'tag']
    list_editable = ['status']
    prepopulated_fields = {'slug': ('name',)}
