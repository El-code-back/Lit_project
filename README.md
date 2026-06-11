# Lit Project — Платформа для онлайн-уроков

Платформа для учителей и учеников, позволяющая публиковать уроки с видео (YouTube, Vimeo, загрузка файлов), заданиями и системой проверки ответов с оценками.

## Функционал

### Для учеников
- Просмотр опубликованных уроков
- Встроенное видео (YouTube, Vimeo, локальные файлы)
- Отправка ответов на задания (текст + файл)
- Простая регистрация (ФИО, группа, email) — без пароля

### Для учителей
- Регистрация и вход по email + пароль
- Создание уроков: заголовок, описание, видео, текст задания, файл задания
- Редактирование и удаление уроков
- Публикация/снятие с публикации уроков
- Просмотр ответов учеников
- Оценка ответов (1–100) с комментарием
- Dashboard со всеми своими уроками

### Технические особенности
- Кастомная модель учителя (`Teacher`) на базе `AbstractUser`, аутентификация по email
- Модель ученика (`Student`) — без пароля, без сессий (простая запись)
- Загрузка видеофайлов до 500 МБ
- HTMX для интерактивности (переключение публикации, удаление)
- SQLite (по умолчанию)

## Стек технологий

- **Backend:** Django 5.0 + Python 3
- **База данных:** SQLite (разработка), легко переключить на PostgreSQL
- **Фронтенд:** Django Templates + CSS
- **Интерактивность:** HTMX (частично)

## Установка и запуск

```bash
# 1. Клонировать репозиторий
git clone https://github.com/El-code-back/Lit_project.git
cd Lit_project

# 2. Создать виртуальное окружение
python -m venv venv

# 3. Активировать окружение
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Установить зависимости
pip install -r requirements.txt

# 5. Настроить переменные окружения
cp .env.example .env
# Отредактируйте .env при необходимости

# 6. Применить миграции
python manage.py migrate

# 7. Создать суперпользователя (опционально)
python manage.py createsuperuser

# 8. Запустить сервер разработки
python manage.py runserver
```

Откройте http://127.0.0.1:8000 в браузере.

## Структура проекта

```
Lit_project/
├── mvp_school/            # Конфигурация Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── lessons/               # Основное приложение
│   ├── models.py          # Teacher, Lesson, Student, Submission, Assignment
│   ├── views.py           # Все view-функции
│   ├── forms.py           # Формы
│   ├── urls.py            # URL-маршруты
│   ├── backends.py        # Email-аутентификация
│   ├── admin.py
│   └── templates/         # HTML-шаблоны
│       ├── base.html
│       ├── index.html
│       ├── lesson_detail.html
│       ├── dashboard.html
│       ├── create_lesson.html
│       ├── login.html
│       ├── register.html
│       ├── student_register.html
│       └── partials/
│           └── lesson_card.html
├── media/                 # Загруженные файлы (игнорируется git)
│   ├── videos/
│   ├── task_files/
│   └── submissions/
├── staticfiles/           # Статика (собирается collectstatic)
├── manage.py
├── requirements.txt
├── .env.example           # Пример конфигурации
└── .gitignore
```

## API / Маршруты

| URL | Описание |
|-----|----------|
| `/` | Главная — список уроков |
| `/lesson/<id>/` | Страница урока |
| `/register/` | Регистрация учителя |
| `/login/` | Вход учителя |
| `/logout/` | Выход учителя |
| `/dashboard/` | Dashboard учителя |
| `/create/` | Создание урока |
| `/lesson/<id>/edit/` | Редактирование урока |
| `/lesson/<id>/delete/` | Удаление урока |
| `/lesson/<id>/toggle-publish/` | Публикация/снять |
| `/submission/<id>/grade/` | Оценить ответ |
| `/student-register/` | Регистрация ученика |
| `/student-logout/` | Сброс сессии ученика |

## Лицензия

MIT
