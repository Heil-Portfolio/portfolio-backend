from django.db import models

class RoadmapItem(models.Model):
    HORIZON_CHOICES = [
        ('short', 'Short Term'),
        ('medium', 'Medium Term'),
        ('long', 'Long Term'),
    ]
    title = models.CharField(max_length=200)
    horizon = models.CharField(max_length=10, choices=HORIZON_CHOICES)
    target_date = models.CharField(max_length=50, help_text="Ex: Q2 2026, 2027")
    done = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['horizon', 'order']

    def __str__(self):
        return f"{'✓' if self.done else '○'} [{self.horizon}] {self.title}"
