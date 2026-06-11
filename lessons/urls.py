from django.urls import path
from . import views

app_name = 'lessons'

urlpatterns = [
    # Public
    path('', views.index, name='index'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    
    # Teacher auth
    path('register/', views.register, name='register'),
    path('login/', views.teacher_login, name='teacher_login'),
    path('logout/', views.teacher_logout, name='teacher_logout'),
    
    # Teacher dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.create_lesson, name='create_lesson'),
    path('lesson/<int:lesson_id>/edit/', views.edit_lesson, name='edit_lesson'),
    path('lesson/<int:lesson_id>/delete/', views.delete_lesson, name='delete_lesson'),
    path('lesson/<int:lesson_id>/toggle-publish/', views.toggle_publish, name='toggle_publish'),
    
    # Student session control
    path('student-logout/', views.student_logout, name='student_logout'),
    
    # Additional
    path('student-register/', views.student_register, name='student_register'),
    path('submission/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),
]
