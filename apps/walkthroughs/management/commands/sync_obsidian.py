from django.core.management.base import BaseCommand
from django.conf import settings
import frontmatter
import os
from apps.walkthroughs.models import Walkthrough
from apps.journal.models import JournalEntry

class Command(BaseCommand):
    help = 'Synchronise le vault Obsidian vers la base de données'

    def handle(self, *args, **kwargs):
        self._sync_walkthroughs()
        self._sync_journal()
        self.stdout.write(self.style.SUCCESS('Sync terminé !'))

    def _sync_walkthroughs(self):
        wt_dir = settings.CONTENT_DIR / 'walkthroughs'
        if not wt_dir.exists():
            self.stdout.write(f'[SKIP] {wt_dir} introuvable')
            return
        for md_file in wt_dir.glob('*.md'):
            if md_file.name.startswith('_'):
                continue
            with open(md_file, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            meta = post.metadata
            slug = meta.get('slug') or md_file.stem
            obj, created = Walkthrough.objects.update_or_create(
                slug=slug,
                defaults={
                    'title': meta.get('title', md_file.stem),
                    'status': meta.get('status', 'draft'),
                    'tags': meta.get('tags', []),
                    'objective': meta.get('objective', ''),
                    'stack': meta.get('stack', ''),
                    'architecture': meta.get('architecture', ''),
                    'problems_encountered': meta.get('problems_encountered', ''),
                    'lessons_learned': meta.get('lessons_learned', []),
                    'reading_time': meta.get('reading_time', 0),
                    'content': post.content,
                    'obsidian_file': f'walkthroughs/{md_file.name}',
                }
            )
            action = 'CREATED' if created else 'UPDATED'
            self.stdout.write(f'[{action}] {slug}')

    def _sync_journal(self):
        journal_dir = settings.CONTENT_DIR / 'journal'
        if not journal_dir.exists():
            self.stdout.write(f'[SKIP] {journal_dir} introuvable')
            return
        for md_file in journal_dir.glob('*.md'):
            if md_file.name.startswith('_'):
                continue
            with open(md_file, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            meta = post.metadata
            slug = meta.get('slug') or md_file.stem
            obj, created = JournalEntry.objects.update_or_create(
                slug=slug,
                defaults={
                    'title': meta.get('title', md_file.stem),
                    'tags': meta.get('tags', []),
                    'content': post.content,
                    'published': meta.get('published', True),
                    'entry_date': meta.get('date', '2026-01-01'),
                    'obsidian_file': f'journal/{md_file.name}',
                }
            )
            action = 'CREATED' if created else 'UPDATED'
            self.stdout.write(f'[{action}] {slug}')
