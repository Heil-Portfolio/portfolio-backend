from django.db import models

class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('current', 'Current'),
        ('learning', 'Learning'),
        ('future', 'Future'),
    ]
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100, blank=True, help_text="Ex: devicon-docker-plain")
    level = models.PositiveIntegerField(default=0, help_text="0 à 100")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='current')
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'order', 'name']

    def __str__(self):
        return f"{self.name} ({self.category}) — {self.level}%"
