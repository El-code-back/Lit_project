from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or update a simple teacher login."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="teacher", help="Teacher login.")
        parser.add_argument("--password", default="LitTeacher2026!", help="Teacher password.")
        parser.add_argument("--email", default="teacher@example.com", help="Teacher email.")
        parser.add_argument("--name", default="Преподаватель литературы", help="Teacher display name.")

    def handle(self, *args, **options):
        Teacher = get_user_model()
        username = options["username"].strip()
        email = options["email"].strip()
        password = options["password"]
        name = options["name"].strip()

        teacher = Teacher.objects.filter(username=username).first()
        if teacher is None:
            teacher = Teacher.objects.filter(email=email).first()

        if teacher is None:
            teacher = Teacher.objects.create_user(
                username=username,
                email=email,
                password=password,
                name=name,
            )
            action = "Created"
        else:
            teacher.username = username
            teacher.email = email
            teacher.name = name or teacher.name
            teacher.set_password(password)
            teacher.save()
            action = "Updated"

        self.stdout.write(self.style.SUCCESS(f"{action} teacher login: {teacher.username}"))
