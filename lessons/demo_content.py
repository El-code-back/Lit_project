from django.contrib.auth import get_user_model

from .assignment_builder import build_assignment_payload
from .models import Assignment, Lesson


SAMPLE_LESSONS = [
    {
        "title": 'И.А. Гончаров. Роман "Обломов"',
        "description": "Образ Обломова, понятие обломовщины и конфликт мечты с действием.",
        "theory_text": """Роман И.А. Гончарова "Обломов" был опубликован в 1859 году и стал одним из ключевых произведений русской литературы XIX века. В центре романа находится Илья Ильич Обломов — герой, который живёт мечтами о спокойной, гармоничной жизни, но почти не способен перейти к действию.

Понятие "обломовщина" связано не только с ленью. Это состояние внутренней остановки, привычка откладывать выбор, страх перед переменами и нежелание принимать ответственность за собственную жизнь. Обломову противопоставлен Штольц: деятельный, рациональный, энергичный герой, который показывает другой жизненный принцип.

Важная линия романа — отношения Обломова и Ольги Ильинской. Через неё раскрывается возможность духовного пробуждения героя, но одновременно становится ясно, что одного чувства недостаточно, если человек не готов измениться.""",
        "video_source_type": "youtube",
        "video_url": "https://www.youtube.com/watch?v=pwpujybUYxY",
        "task_text": "Посмотрите видео и прочитайте теорию. Объясните, почему слово «обломовщина» стало нарицательным, и приведите два аргумента из материала урока.",
        "assignment_title": 'Проверка понимания романа "Обломов"',
        "assignment_type": "short",
        "manual_questions": """Что означает понятие "обломовщина"?
Почему Штольц противопоставлен Обломову?
Как линия Ольги Ильинской помогает раскрыть характер главного героя?""",
    },
    {
        "title": "Л.Н. Толстой. Жизнь и творчество",
        "description": "Биография Толстого, главные произведения и нравственные вопросы его творчества.",
        "theory_text": """Лев Николаевич Толстой — один из крупнейших русских писателей XIX века. Его творчество соединяет художественную масштабность, глубокий психологизм и нравственный поиск. Важными этапами его биографии стали детство в Ясной Поляне, служба на Кавказе, участие в Крымской войне и дальнейшая литературная работа.

Ранние произведения Толстого связаны с автобиографической трилогией "Детство", "Отрочество", "Юность". Позже он создаёт эпические произведения "Война и мир" и "Анна Каренина", в которых исследует семью, историю, личный выбор и внутреннюю жизнь человека.

Для Толстого особенно важны вопросы совести, нравственного совершенствования, отношения человека к обществу и правде. Его герои часто проходят путь духовного поиска: ошибаются, сомневаются, меняются и пытаются понять, как жить честно.""",
        "video_source_type": "rutube",
        "video_url": "https://rutube.ru/video/b8aa9188d21f4493da75290d0753f7a1/",
        "task_text": "После просмотра видео составьте краткую хронологию жизни Толстого и объясните, какие нравственные вопросы были важны для его творчества.",
        "assignment_title": "Л.Н. Толстой: биография и темы творчества",
        "assignment_type": "test",
        "manual_questions": """Толстой соединяет художественное повествование с нравственным поиском.
Ранние произведения Толстого связаны с трилогией "Детство", "Отрочество", "Юность".
Для Толстого важны вопросы совести, правды и внутреннего выбора.""",
    },
]


def get_sample_teacher():
    Teacher = get_user_model()
    teacher = Teacher.objects.filter(email="teacher@example.com").first()
    if teacher:
        return teacher

    return Teacher.objects.create_user(
        username="teacher@example.com",
        email="teacher@example.com",
        password="TeacherPass123!",
        name="Преподаватель литературы",
    )


def create_sample_lessons(force=False):
    teacher = get_sample_teacher()
    created_or_updated = []

    for item in SAMPLE_LESSONS:
        lesson, created = Lesson.objects.update_or_create(
            teacher=teacher,
            title=item["title"],
            defaults={
                "description": item["description"],
                "theory_text": item["theory_text"],
                "video_source_type": item["video_source_type"],
                "video_url": item["video_url"],
                "task_text": item["task_text"],
                "is_published": True,
            },
        )

        if created or force or not lesson.assignments.filter(is_active=True).exists():
            lesson.assignments.update(is_active=False)
            Assignment.objects.create(
                lesson=lesson,
                title=item["assignment_title"],
                source_text=item["theory_text"],
                assignment_type=item["assignment_type"],
                generated=build_assignment_payload(
                    item["assignment_type"],
                    item["theory_text"],
                    item["manual_questions"],
                ),
                is_active=True,
            )

        created_or_updated.append(lesson)

    return created_or_updated
