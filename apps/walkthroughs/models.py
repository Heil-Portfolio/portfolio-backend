from django.db import models

class Walkthrough(models.Model):
    STATUS_CHOICES = [
        ('published', 'Published'),
        ('draft', 'Draft'),
        ('planned', 'Planned'),
    ]
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    tags = models.JSONField(default=list, help_text="['Docker', 'AWS', 'Nginx']")
    objective = models.TextField(help_text="Ce que tu voulais accomplir")
    stack = models.CharField(max_length=300)
    architecture = models.TextField(blank=True)
    problems_encountered = models.TextField(blank=True)
    lessons_learned = models.JSONField(default=list)
    # Contenu markdown libre (Obsidian)
    content = models.TextField(blank=True, help_text="Markdown complet — étapes, code, screenshots")
    obsidian_file = models.CharField(max_length=500, blank=True,
        help_text="Chemin relatif dans le vault : walkthroughs/aws-ec2.md")
    reading_time = models.PositiveIntegerField(default=0, help_text="Minutes")
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title
