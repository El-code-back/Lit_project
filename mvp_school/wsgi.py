import os
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mvp_school.settings')
application = get_wsgi_application()


def prepare_vercel_database():
    if not getattr(settings, 'IS_VERCEL', False):
        return

    if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
        database_path = Path(settings.DATABASES['default']['NAME'])
        bundled_database_path = settings.BASE_DIR / 'db.sqlite3'
        database_path.parent.mkdir(parents=True, exist_ok=True)

        if not database_path.exists() and bundled_database_path.exists():
            shutil.copy2(bundled_database_path, database_path)

    call_command('migrate', interactive=False, verbosity=0)


def seed_empty_database():
    if not getattr(settings, 'SEED_SAMPLE_LESSONS', False):
        return

    from lessons.demo_content import create_sample_lessons
    from lessons.models import Lesson

    if not Lesson.objects.exists():
        create_sample_lessons()


prepare_vercel_database()
seed_empty_database()
