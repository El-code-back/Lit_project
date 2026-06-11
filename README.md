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

## Деплой на Render (бесплатно)

Самый простой и быстрый способ запустить проект в продакшене.

### Способ 1: Через render.yaml (автоматически)

1. Зайдите на [dashboard.render.com](https://dashboard.render.com) и нажмите **"New +" → "Blueprint"**
2. Выберите ваш репозиторий `El-code-back/Lit_project`
3. Render сам прочитает `render.yaml` и создаст Web Service
4. В появившемся окне **заполните переменную `SECRET_KEY`**:
   - Нажмите `Generate` рядом с SECRET_KEY (или вставьте свой)
   - Render автоматически запишет её в secrets
5. Нажмите **"Apply"**

Render сам:
- Установит зависимости
- Соберёт статику через `collectstatic`
- Применит миграции
- Запустит сервер через gunicorn
- Создаст постоянный диск 1 ГБ для `media/` (загруженные файлы)

Через 2–3 минуты сайт будет доступен по адресу `https://lit-project.onrender.com`

### Способ 2: Вручную через Web Service

1. На [dashboard.render.com](https://dashboard.render.com) нажмите **"New +" → "Web Service"**
2. Подключите GitHub и выберите `El-code-back/Lit_project`
3. Заполните поля:
   - **Name:** `lit-project`
   - **Region:** `Frankfurt (EU)` — ближайший к Средней Азии
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:**
     ```
     pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
     ```
   - **Start Command:**
     ```
     gunicorn mvp_school.wsgi --bind 0.0.0.0:$PORT --workers 4 --timeout 120
     ```
   - **Plan:** `Free`
4. Добавьте переменные окружения (см. ниже)
5. Добавьте **Persistent Disk** (постоянный диск для файлов):
   - Нажмите **"Add Disk"**
   - **Name:** `media`
   - **Mount Path:** `/opt/render/project/src/media`
   - **Size:** `1 GB`
6. Нажмите **"Create Web Service"**

### Переменные окружения на Render

| Переменная | Значение | Где взять |
|---|---|---|
| `SECRET_KEY` | (секретный ключ) | Нажмите **Generate** на Render |
| `DEBUG` | `False` | — |
| `ALLOWED_HOSTS` | `.onrender.com` | — |
| `CSRF_TRUSTED_ORIGINS` | `https://lit-project.onrender.com` | — |
| `PYTHON_VERSION` | `3.13.7` | — |

### После деплоя

1. Откройте `https://lit-project.onrender.com/admin/` и создайте суперпользователя через **Django Admin**
2. Или зарегистрируйтесь через `/register/` на самом сайте
3. Загрузите видео и создайте уроки через `/dashboard/`

### Важно

- Бесплатный тариф Render "засыпает" сервер после 15 минут бездействия. Первый запрос после просыпания может длиться до 30 секунд.
- SQLite работает на бесплатном диске, но для продакшена с нагрузкой лучше перейти на PostgreSQL (Render предоставляет его бесплатно).
- Загруженные файлы (`media/`) хранятся на постоянном диске и **не пропадают** после перезапуска.

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
