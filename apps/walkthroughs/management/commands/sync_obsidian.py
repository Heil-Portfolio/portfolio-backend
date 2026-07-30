from django.core.management.base import BaseCommand
from django.conf import settings
import frontmatter
import os
import re
import cloudinary
import cloudinary.uploader
from datetime import datetime, timezone
from apps.walkthroughs.models import Walkthrough
from apps.journal.models import JournalEntry

# Repère les images markdown : ![alt](chemin)
IMAGE_PATTERN = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')


def _parse_date(value):
    """Parse le champ `date` du frontmatter (str 'YYYY-MM-DD' ou objet date/datetime)
    en datetime timezone-aware. Retourne None si absent/invalide."""
    if not value:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    try:
        # frontmatter/PyYAML retourne parfois un objet `date` (pas `datetime`)
        if hasattr(value, 'year') and not isinstance(value, str):
            return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
        return datetime.strptime(str(value), '%Y-%m-%d').replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def _upload_and_rewrite_images(content, base_dir, cloudinary_folder, stdout):
    """Pour chaque image locale référencée dans le markdown, l'upload vers
    Cloudinary (idempotent : même public_id = écrasement, pas de doublon)
    et remplace le chemin local par l'URL Cloudinary."""
    def repl(match):
        alt, path = match.group(1), match.group(2)
        if path.startswith(('http://', 'https://')):
            return match.group(0)  # déjà une URL absolue, on ne touche pas
        local_path = base_dir / path
        if not local_path.exists():
            stdout.write(f'  [WARN] image introuvable, ignorée : {local_path}')
            return match.group(0)
        public_id = f'{cloudinary_folder}/{local_path.stem}'
        try:
            result = cloudinary.uploader.upload(
                str(local_path),
                public_id=public_id,
                overwrite=True,
                unique_filename=False,
            )
        except Exception as e:
            stdout.write(f'  [ERROR] upload Cloudinary échoué pour {local_path.name} : {e}')
            return match.group(0)
        return f'![{alt}]({result["secure_url"]})'
    return IMAGE_PATTERN.sub(repl, content)


class Command(BaseCommand):
    help = 'Synchronise le vault Obsidian vers la base de données'

    def handle(self, *args, **kwargs):
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True,
        )
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
            content = _upload_and_rewrite_images(
                post.content, wt_dir, f'portfolio/walkthroughs/{slug}', self.stdout
            )
            published_at = _parse_date(meta.get('date'))
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
                    'content': content,
                    'obsidian_file': f'walkthroughs/{md_file.name}',
                    'published_at': published_at,
                }
            )
            action = 'CREATED' if created else 'UPDATED'
            self.stdout.write(f'[{action}] {slug}' + (f' (date: {published_at.date()})' if published_at else ' (⚠ pas de champ `date` dans le frontmatter)'))

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
