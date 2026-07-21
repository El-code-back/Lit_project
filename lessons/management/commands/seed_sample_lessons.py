from django.core.management.base import BaseCommand

from lessons.demo_content import create_sample_lessons


class Command(BaseCommand):
    help = "Create starter literature lessons as normal database records."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Recreate active assignments for the sample lessons.",
        )

    def handle(self, *args, **options):
        lessons = create_sample_lessons(force=options["force"])
        for lesson in lessons:
            self.stdout.write(self.style.SUCCESS(f"Ready: {lesson.title}"))
