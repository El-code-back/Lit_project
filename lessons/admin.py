from django.contrib import admin
from .models import Teacher, Lesson, Submission, Assignment

admin.site.register(Teacher)
admin.site.register(Lesson)
admin.site.register(Submission)
admin.site.register(Assignment)
