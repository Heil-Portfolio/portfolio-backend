from django.db import models

class Project(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('planned', 'Planned'),
        ('archived', 'Archived'),
    ]
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    description = models.TextField()
    architecture = models.TextField(blank=True)
    stack = models.JSONField(default=list, help_text="['Django', 'Docker']")
    highlights = models.JSONField(default=list, help_text="['JWT Auth', 'Multi-tenant']")
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.name
