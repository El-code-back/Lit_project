from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class Teacher(AbstractUser):
    """Учитель (расширенный User)"""
    name = models.CharField("Имя", max_length=200)
    email = models.EmailField("Email", unique=True)
    phone = models.CharField("Телефон", max_length=20, blank=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    
    class Meta:
        verbose_name = "Учитель"
        verbose_name_plural = "Учителя"
    
    def __str__(self):
        return self.name or self.username

class Lesson(models.Model):
    """Урок"""
    VIDEO_SOURCE_CHOICES = [
        ('youtube', 'YouTube'),
        ('vimeo', 'Vimeo'),
        ('rutube', 'Rutube'),
        ('upload', 'Файл'),
    ]
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField("Название урока", max_length=300)
    description = models.TextField("Описание", blank=True)
    theory_text = models.TextField("Теория урока", blank=True)
    
    # Видео
    video_source_type = models.CharField("Источник видео", max_length=10, choices=VIDEO_SOURCE_CHOICES)
    video_url = models.URLField("URL видео (YouTube/Vimeo)", blank=True, null=True)
    video_file = models.FileField("Видео файл", upload_to='videos/', blank=True, null=True)
    
    # Задание
    task_text = models.TextField("Текст задания")
    task_file = models.FileField("Файл задания", upload_to='task_files/', blank=True, null=True)
    
    # Статус
    is_published = models.BooleanField("Опубликован", default=True)
    published_at = models.DateTimeField("Опубликован в", auto_now_add=True)
    
    # Даты
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлён", auto_now=True)
    
    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_video_url(self):
        """Возвращает URL видео для отображения"""
        if self.video_source_type == 'youtube' and self.video_url:
            # Handle standard watch links: youtube.com/watch?v=ID
            # Handle short links: youtu.be/ID
            # Handle embeds: youtube.com/embed/ID
            video_id = None
            if 'v=' in self.video_url:
                video_id = self.video_url.split('v=')[-1].split('&')[0]
            elif 'youtu.be/' in self.video_url:
                video_id = self.video_url.split('youtu.be/')[-1].split('?')[0]
            elif 'embed/' in self.video_url:
                video_id = self.video_url.split('embed/')[-1].split('?')[0]
            
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}"
            return self.video_url
        elif self.video_source_type == 'vimeo' and self.video_url:
            video_id = self.video_url.split('/')[-1].split('?')[0]
            if video_id:
                return f"https://player.vimeo.com/video/{video_id}"
            return self.video_url
        elif self.video_source_type == 'rutube' and self.video_url:
            video_id = self.video_url.rstrip('/').split('/')[-1].split('?')[0]
            if video_id:
                return f"https://rutube.ru/play/embed/{video_id}/"
            return self.video_url
        elif self.video_source_type == 'upload' and self.video_file:
            return self.video_file.url  # Локальный файл
        return None

    def is_local_video(self):
        """Является ли видео локальным файлом"""
        return self.video_source_type == 'upload' and self.video_file

    def get_video_embed_url(self):
        """Возвращает embed URL для обратной совместимости"""
        return self.get_video_url()

class Student(models.Model):
    """Ученик (простая регистрация)"""
    name = models.CharField("ФИО", max_length=200)
    group = models.CharField("Группа", max_length=100)
    email = models.EmailField("Email")
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    
    class Meta:
        verbose_name = "Ученик"
        verbose_name_plural = "Ученики"
    
    def __str__(self):
        return f"{self.name} ({self.group})"

class Submission(models.Model):
    """Ответ ученика"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='submissions')
    student_name = models.CharField("Имя ученика", max_length=200)
    student_group = models.CharField("Группа", max_length=100, blank=True)
    student_email = models.EmailField("Email", blank=True)
    answer_text = models.TextField("Текст ответа", blank=True)
    answer_file = models.FileField("Файл ответа", upload_to='submissions/', blank=True, null=True)
    answer_data = models.JSONField("Ответы на задание", default=dict, blank=True)
    
    # Новая: Оценка от учителя
    grade = models.IntegerField("Оценка", blank=True, null=True, 
                                help_text="Оценка от 1 до 100")
    grade_comment = models.TextField("Комментарий к оценке", blank=True)
    
    submitted_at = models.DateTimeField("Отправлено", auto_now_add=True)
    graded_at = models.DateTimeField("Оценено", blank=True, null=True)
    
    class Meta:
        verbose_name = "Ответ ученика"
        verbose_name_plural = "Ответы учеников"
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.student_name} - {self.lesson.title}"


class Assignment(models.Model):
    """Задание, привязанное к уроку. Для MVP содержит тип и сгенерированные вопросы."""
    TYPE_CHOICES = [
        ('test', 'Тест (множественный выбор)'),
        ('fill', 'Заполнить пропуски'),
        ('short', 'Краткий ответ'),
        ('theory', 'Теория / чтение'),
    ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField('Название задания', max_length=255, blank=True)
    source_text = models.TextField('Источник (вставьте текст)', blank=True)
    assignment_type = models.CharField('Тип задания', max_length=20, choices=TYPE_CHOICES)
    generated = models.JSONField('Сгенерированные вопросы/данные', default=dict, blank=True)
    order = models.PositiveIntegerField('Порядок', default=1)
    is_active = models.BooleanField('Активно', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.title or f"Задание {self.id} ({self.get_assignment_type_display()})"

    def items(self):
        return self.generated.get('items', []) if isinstance(self.generated, dict) else []
