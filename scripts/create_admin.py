import os
import django
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mvp_school.settings')
django.setup()
from lessons.models import Teacher
import secrets

email = 'snekkincoop@gmail.com'
if Teacher.objects.filter(email=email).exists():
    u = Teacher.objects.get(email=email)
    print('EXISTS', u.id, u.username, u.email, 'is_staff=' + str(u.is_staff), 'is_superuser=' + str(u.is_superuser))
else:
    pw = secrets.token_urlsafe(10)
    u = Teacher.objects.create_user(username=email, email=email, password=pw)
    u.name = 'Snekkin Coop'
    u.is_staff = True
    u.is_superuser = True
    u.save()
    print('CREATED', u.id, u.username, u.email, 'password=' + pw, 'is_staff=' + str(u.is_staff), 'is_superuser=' + str(u.is_superuser))
