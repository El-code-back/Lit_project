from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse
from .assignment_builder import build_assignment_payload
from .models import Teacher, Lesson, Submission, Assignment
from django.conf import settings
from .forms import RegistrationForm, LoginForm, CreateLessonForm, SubmissionForm

EMAIL_AUTH_BACKEND = 'lessons.backends.EmailBackend'

# === PUBLIC PAGES ===

def index(request):
    """Главная: список опубликованных уроков"""
    lessons = Lesson.objects.filter(is_published=True)
    return render(request, 'index.html', {'lessons': lessons})

def healthz(request):
    """Проверка состояния приложения для внешнего мониторинга"""
    return HttpResponse('OK', content_type='text/plain')


def save_assignment_from_form(lesson, form):
    assignment_type = form.cleaned_data.get('assignment_type')
    if not assignment_type:
        lesson.assignments.update(is_active=False)
        return None

    source_text = form.cleaned_data.get('assignment_source_text', '')
    manual_questions = form.cleaned_data.get('assignment_manual_questions', '')
    generated = build_assignment_payload(assignment_type, source_text, manual_questions)
    assignment = lesson.assignments.filter(is_active=True).first()
    if assignment is None:
        assignment = Assignment(lesson=lesson)

    assignment.title = form.cleaned_data.get('assignment_title') or 'Задание к уроку'
    assignment.assignment_type = assignment_type
    assignment.source_text = source_text
    assignment.generated = generated
    assignment.is_active = True
    assignment.save()
    return assignment


def assignment_initial_data(lesson):
    assignment = lesson.assignments.filter(is_active=True).first()
    if not assignment:
        return {}
    return {
        'assignment_title': assignment.title,
        'assignment_type': assignment.assignment_type,
        'assignment_source_text': assignment.source_text,
        'assignment_manual_questions': "\n".join(item.get('prompt', '') for item in assignment.items()),
    }


def collect_assignment_answers(request, assignment):
    if not assignment:
        return {}
    answers = {}
    for item in assignment.items():
        item_id = item.get('id')
        if item_id:
            answers[item_id] = request.POST.get(f'assignment_{item_id}', '').strip()
    return answers


def evaluate_assignment(assignment, answers):
    if not assignment:
        return None

    auto_items = [item for item in assignment.items() if item.get('type') in {'test', 'fill'}]
    if not auto_items or len(auto_items) != len(assignment.items()):
        return None

    correct = 0
    for item in auto_items:
        expected = str(item.get('answer', '')).strip().lower()
        actual = str(answers.get(item.get('id'), '')).strip().lower()
        if expected and actual == expected:
            correct += 1

    total = len(auto_items)
    return {
        'correct': correct,
        'total': total,
        'grade': round(correct / total * 100) if total else None,
    }


def lesson_detail(request, lesson_id):
    """Страница урока для ученика"""
    lesson = get_object_or_404(Lesson, id=lesson_id, is_published=True)
    assignment = lesson.assignments.filter(is_active=True).first()
    
    # Проверка: является ли пользователь учителем этого урока
    is_teacher = request.user.is_authenticated and request.user.lessons.filter(id=lesson.id).exists()
    
    if request.method == 'POST' and not is_teacher:
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['student_name']
            group = form.cleaned_data['group']
            email = form.cleaned_data['email']
            
            from .models import Student
            Student.objects.get_or_create(
                email=email,
                defaults={'name': name, 'group': group}
            )
            
            # Сохраняем сессию
            request.session['student_name'] = name
            request.session['student_group'] = group
            request.session['student_email'] = email
            answer_data = collect_assignment_answers(request, assignment)
            auto_result = evaluate_assignment(assignment, answer_data)
            
            submission = Submission(
                lesson=lesson,
                student_name=name,
                student_group=group,
                student_email=email,
                answer_text=form.cleaned_data.get('answer_text', ''),
                answer_file=form.cleaned_data.get('answer_file'),
                answer_data=answer_data,
            )
            if auto_result and auto_result.get('grade') is not None:
                submission.grade = auto_result['grade']
                submission.grade_comment = f"Автопроверка: {auto_result['correct']} из {auto_result['total']}"
                submission.graded_at = timezone.now()
            submission.save()
            return redirect('lessons:lesson_detail', lesson_id=lesson.id)
    else:
        initial_data = {
            'student_name': request.session.get('student_name', ''),
            'group': request.session.get('student_group', ''),
            'email': request.session.get('student_email', ''),
        }
        form = SubmissionForm(initial=initial_data)

    latest_submission = None
    student_email = request.session.get('student_email')
    if student_email:
        latest_submission = lesson.submissions.filter(student_email=student_email).first()
    
    embed_url = lesson.get_video_url()
    iframe_src = embed_url
    watch_url = lesson.video_url or embed_url
    embed_nocookie = None
    if embed_url and lesson.video_source_type == 'youtube':
        origin = request.scheme + '://' + request.get_host()
        iframe_src = f"{embed_url}?rel=0&modestbranding=1&origin={origin}"
        embed_nocookie = embed_url.replace('www.youtube.com/embed/', 'www.youtube-nocookie.com/embed/')
        if lesson.video_url:
            watch_url = lesson.video_url
    elif embed_url and lesson.video_source_type == 'vimeo':
        iframe_src = f"{embed_url}?badge=0&autopause=1&muted=0"
        watch_url = lesson.video_url or embed_url

    return render(request, 'lesson_detail.html', {
        'lesson': lesson,
        'form': form,
        'is_teacher': is_teacher,
        'embed_url': embed_url,
        'iframe_src': iframe_src,
        'watch_url': watch_url,
        'embed_nocookie': embed_nocookie,
        'debug': settings.DEBUG,
        'assignment': assignment,
        'latest_submission': latest_submission,
    })

def student_register(request):
    """Регистрация ученика (простая, без пароля)"""
    if request.method == 'POST':
        form = SubmissionForm(request.POST)
        name = request.POST.get('student_name') or request.POST.get('name')
        group = request.POST.get('group')
        email = request.POST.get('email')
        
        if name and group and email:
            from .models import Student
            Student.objects.get_or_create(
                email=email,
                defaults={'name': name, 'group': group}
            )
            # Создаем "студента" как сессию
            request.session['student_name'] = name
            request.session['student_group'] = group
            request.session['student_email'] = email
            return redirect('lessons:index')
    
    initial = {
        'student_name': request.session.get('student_name', ''),
        'group': request.session.get('student_group', ''),
        'email': request.session.get('student_email', ''),
    }
    form = SubmissionForm(initial=initial)
    return render(request, 'student_register.html', {'form': form})

@login_required
def grade_submission(request, submission_id):
    """Оценка ответа ученика учителем"""
    submission = get_object_or_404(Submission, id=submission_id)
    lesson = submission.lesson
    
    # Проверка: только владелец урока
    if lesson.teacher != request.user:
        return redirect('lessons:dashboard')
    
    if request.method == 'POST':
        grade_val = request.POST.get('grade')
        if grade_val:
            try:
                grade = int(grade_val)
            except ValueError:
                return redirect('lessons:dashboard')
            comment = request.POST.get('comment', '')
            
            if 1 <= grade <= 100:
                submission.grade = grade
                submission.grade_comment = comment
                submission.graded_at = timezone.now()
                submission.save()
    
    return redirect('lessons:dashboard')

# === TEACHER AUTH ===

def register(request):
    """Регистрация учителя (форма на сайте)"""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            teacher = form.save()
            login(request, teacher, backend=EMAIL_AUTH_BACKEND)
            return redirect('lessons:dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def teacher_login(request):
    """Вход учителя"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login_value = form.cleaned_data['login'].strip()
            password = form.cleaned_data['password']
            user = authenticate(request, username=login_value, password=password)
            if user is None and '@' in login_value:
                user = authenticate(request, email=login_value, password=password)
            if user:
                login(request, user)
                for key in ('student_name', 'student_group', 'student_email'):
                    request.session.pop(key, None)
                return redirect('lessons:dashboard')
            else:
                form.add_error(None, 'Неверный логин или пароль')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def teacher_logout(request):
    """Выход"""
    logout(request)
    for key in ('student_name', 'student_group', 'student_email'):
        request.session.pop(key, None)
    return redirect('lessons:index')


def student_logout(request):
    """Очистить ученический профиль из сессии"""
    for key in ('student_name', 'student_group', 'student_email'):
        request.session.pop(key, None)
    return redirect('lessons:index')

# === TEACHER DASHBOARD ===

@login_required
def dashboard(request):
    """Dashboard учителя: список своих уроков"""
    lessons = request.user.lessons.prefetch_related('submissions', 'assignments').all()
    submissions = Submission.objects.filter(lesson__teacher=request.user).select_related('lesson')
    pending_count = submissions.filter(grade__isnull=True).count()
    checked_count = submissions.filter(grade__isnull=False).count()
    return render(request, 'dashboard.html', {
        'lessons': lessons,
        'submissions': submissions[:12],
        'pending_count': pending_count,
        'checked_count': checked_count,
    })

@login_required
def create_lesson(request):
    """Создание урока"""
    if request.method == 'POST':
        form = CreateLessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.teacher = request.user
            lesson.is_published = True
            lesson.save()
            save_assignment_from_form(lesson, form)
            return redirect('lessons:dashboard')
    else:
        form = CreateLessonForm()
    return render(request, 'create_lesson.html', {'form': form})

@login_required
def edit_lesson(request, lesson_id):
    """Редактирование урока"""
    lesson = get_object_or_404(Lesson, id=lesson_id, teacher=request.user)
    if request.method == 'POST':
        form = CreateLessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            lesson = form.save()
            save_assignment_from_form(lesson, form)
            return redirect('lessons:dashboard')
    else:
        form = CreateLessonForm(instance=lesson, initial=assignment_initial_data(lesson))
    return render(request, 'create_lesson.html', {'form': form, 'lesson': lesson})


@login_required
def delete_lesson(request, lesson_id):
    """Удаление урока"""
    lesson = get_object_or_404(Lesson, id=lesson_id, teacher=request.user)
    if request.method == 'POST':
        lesson.delete()
        if request.headers.get('HX-Request'):
            from django.http import HttpResponse
            return HttpResponse("")  # Empty response triggers removal of target in HTMX
        return redirect('lessons:dashboard')
    return redirect('lessons:dashboard')

@login_required
def toggle_publish(request, lesson_id):
    """Toggle публикации урока"""
    lesson = get_object_or_404(Lesson, id=lesson_id, teacher=request.user)
    lesson.is_published = not lesson.is_published
    if lesson.is_published:
        lesson.published_at = timezone.now()
    lesson.save()
    
    if request.headers.get('HX-Request'):
        return render(request, 'partials/lesson_card.html', {'lesson': lesson})
    return redirect('lessons:dashboard')
