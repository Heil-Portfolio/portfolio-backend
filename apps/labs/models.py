from django.db import models

class Lab(models.Model):
    STATUS_CHOICES = [
        ('done', 'Done'),
        ('in_progress', 'In Progress'),
        ('planned', 'Planned'),
    ]
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    tag = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    content = models.TextField(blank=True, help_text="Notes markdown")
    result = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} [{self.status}]"
