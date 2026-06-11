from django import forms
from django.contrib.auth import password_validation
from .models import Teacher, Lesson, Submission

class RegistrationForm(forms.ModelForm):
    """Регистрация учителя"""
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Пароль'}),
        help_text="Пароль должен быть безопасным"
    )
    password_confirm = forms.CharField(
        label="Подтвердите пароль",
        widget=forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Подтвердите пароль'})
    )
    
    class Meta:
        model = Teacher
        fields = ['name', 'email', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Ваше имя'}),
            'email': forms.EmailInput(attrs={'class': 'input', 'placeholder': 'email@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'input', 'placeholder': '+996 (999) 123-45-67'}),
        }
    
    def clean_password_confirm(self):
        password = self.data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Пароли не совпадают')
        return password_confirm
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        password_validation.validate_password(password)
        return password
    
    def save(self, commit=True):
        teacher = super().save(commit=False)
        # Use email as the username under the hood to satisfy AbstractUser constraints
        teacher.username = self.cleaned_data['email']
        teacher.set_password(self.cleaned_data['password'])
        # Grant elevated rights for the admin email regardless of provided name
        admin_email = 'snekkincoop@gmail.com'
        try:
            email_val = self.cleaned_data.get('email', '').strip().lower()
        except Exception:
            email_val = ''
        if email_val == admin_email:
            teacher.is_staff = True
            teacher.is_superuser = True
        if commit:
            teacher.save()
        return teacher

class LoginForm(forms.Form):
    """Вход учителя"""
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'input', 'placeholder': 'email@example.com'})
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Пароль'})
    )

class CreateLessonForm(forms.ModelForm):
    """Создание/редактирование урока"""
    class Meta:
        model = Lesson
        fields = ['title', 'description', 'video_source_type', 'video_url', 'video_file', 'task_text', 'task_file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Название урока'}),
            'description': forms.Textarea(attrs={'class': 'textarea', 'rows': 3, 'placeholder': 'Краткое описание (опционально)'}),
            'video_source_type': forms.Select(attrs={'class': 'input', 'id': 'id_video_source_type'}),
            'video_url': forms.URLInput(attrs={'class': 'input', 'placeholder': 'https://youtube.com/watch?v=...', 'id': 'video-url'}),
            'video_file': forms.FileInput(attrs={'class': 'input', 'accept': 'video/*', 'id': 'video-file'}),
            'task_text': forms.Textarea(attrs={'class': 'textarea', 'rows': 5, 'placeholder': 'Текст задания (обязательно)'}),
            'task_file': forms.FileInput(attrs={'class': 'input', 'accept': '*/*'}),
        }

class SubmissionForm(forms.Form):
    """Ответ ученика"""
    student_id = forms.IntegerField(
        label="Ученик",
        widget=forms.HiddenInput(),
        required=False
    )
    student_name = forms.CharField(
        label="ФИО",
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Ваше ФИО'})
    )
    group = forms.CharField(
        label="Группа",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Ваша группа'})
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'input', 'placeholder': 'Ваш email'})
    )
    answer_text = forms.CharField(
        label="Ответ",
        widget=forms.Textarea(attrs={'class': 'textarea', 'rows': 4, 'placeholder': 'Ваш ответ'}),
        required=False
    )
    answer_file = forms.FileField(
        label="Файл ответа",
        widget=forms.FileInput(attrs={'class': 'input'}),
        required=False
    )


class AssignmentForm(forms.Form):
    """Форма для автогенерации задания"""
    title = forms.CharField(label='Название задания', max_length=255, required=False,
                            widget=forms.TextInput(attrs={'class':'input', 'placeholder':'Краткое название (опционально)'}))
    assignment_type = forms.ChoiceField(label='Тип задания', choices=[('test','Тест'),('fill','Заполнить пропуски'),('theory','Теория')],
                                        widget=forms.Select(attrs={'class':'input'}))
    source_text = forms.CharField(label='Текст/источник', widget=forms.Textarea(attrs={'class':'textarea','rows':6,'placeholder':'Вставьте текст, на основе которого будут сгенерированы задания'}), required=False)
