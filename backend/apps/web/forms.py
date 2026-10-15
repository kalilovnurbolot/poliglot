from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from apps.grammar.models import GrammarRule
from apps.users.models import User
from apps.vocabulary.models import Word

INPUT = 'input'


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': INPUT, 'placeholder': 'Email', 'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': INPUT, 'placeholder': 'Пароль'}))

    def __init__(self, request, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        if self.errors:
            return cleaned
        self.user = authenticate(self.request, email=cleaned['email'], password=cleaned['password'])
        if self.user is None:
            raise forms.ValidationError('Неверный email или пароль')
        return cleaned


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': INPUT, 'placeholder': 'Пароль'}))

    class Meta:
        model = User
        fields = ['first_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Имя'}),
            'email': forms.EmailInput(attrs={'class': INPUT, 'placeholder': 'Email'}),
        }

    def clean_password(self):
        password = self.cleaned_data['password']
        validate_password(password, User(email=self.cleaned_data.get('email', '')))
        return password

    def save(self, commit=True):
        return User.objects.create_user(
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
        )


class WordForm(forms.ModelForm):
    class Meta:
        model = Word
        fields = ['text', 'translation', 'transcription', 'part_of_speech', 'level', 'example_sentence']
        widgets = {
            'text': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Слово'}),
            'translation': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Перевод'}),
            'transcription': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Транскрипция (необязательно)'}),
            'part_of_speech': forms.Select(attrs={'class': INPUT}),
            'level': forms.Select(attrs={'class': f'{INPUT} self-start'}),
            'example_sentence': forms.Textarea(
                attrs={'class': INPUT, 'rows': 2, 'placeholder': 'Пример предложения (необязательно)'}
            ),
        }

    PART_OF_SPEECH_LABELS = {
        'noun': 'существительное',
        'verb': 'глагол',
        'adjective': 'прилагательное',
        'adverb': 'наречие',
        'phrase': 'фраза',
        'other': 'другое',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['part_of_speech'].choices = list(self.PART_OF_SPEECH_LABELS.items())
        self.fields['level'].choices = [(c, f'Уровень {c}') for c, _ in Word._meta.get_field('level').choices]

    def clean(self):
        cleaned = super().clean()
        for name in ('text', 'translation', 'transcription', 'example_sentence'):
            if isinstance(cleaned.get(name), str):
                cleaned[name] = cleaned[name].strip()
        return cleaned


class GrammarRuleForm(forms.ModelForm):
    class Meta:
        model = GrammarRule
        fields = ['title', 'level', 'body']
        widgets = {
            'title': forms.TextInput(attrs={'class': f'flex-1 {INPUT}', 'placeholder': 'Название правила'}),
            'level': forms.Select(attrs={'class': INPUT}),
            'body': forms.Textarea(attrs={
                'class': f'{INPUT} block w-full min-h-[480px] font-mono text-[13px] leading-relaxed',
                'spellcheck': 'false',
                'data-rule-body': '',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['level'].choices = [(c, f'Уровень {c}') for c, _ in GrammarRule._meta.get_field('level').choices]

    def clean_title(self):
        return self.cleaned_data['title'].strip()
