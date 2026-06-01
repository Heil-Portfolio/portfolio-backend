from django.db import models

class JournalEntry(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    tags = models.JSONField(default=list)
    content = models.TextField(help_text="Markdown — notes, erreurs, découvertes")
    obsidian_file = models.CharField(max_length=500, blank=True)
    published = models.BooleanField(default=True)
    entry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-entry_date']

    def __str__(self):
        return f"{self.entry_date} — {self.title}"
