import zoneinfo

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone

from apps.club.models import ClubSession, InstagramBot
from apps.core.models import SiteSettings
from apps.grammar.models import GrammarRule
from apps.users.models import User
from apps.vocabulary.models import Deck, Word

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
            blocked = User.objects.filter(email__iexact=cleaned['email'], is_active=False).first()
            if blocked and blocked.check_password(cleaned['password']):
                raise forms.ValidationError('Аккаунт заблокирован. Обратитесь к администратору.')
            raise forms.ValidationError('Неверный email или пароль')
        return cleaned


class WordListForm(forms.Form):
    """Many words at once, pasted as text (word_list.parse_word_list)."""
    text = forms.CharField(widget=forms.Textarea(attrs={
        'class': INPUT, 'rows': 8,
        'placeholder': 'achieve — достигать\navoid — избегать\n\nКаждое слово с новой строки. Заголовки вроде «Verbs» или «Adjectives» задают часть речи.',
    }))
    part_of_speech = forms.ChoiceField(widget=forms.Select(attrs={'class': INPUT}))
    level = forms.ChoiceField(widget=forms.Select(attrs={'class': INPUT}))
    deck = forms.ModelChoiceField(queryset=Deck.objects.none(), empty_label=None, widget=forms.Select(attrs={'class': INPUT}))

    def __init__(self, *args, decks, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['deck'].queryset = decks
        self.fields['part_of_speech'].choices = [
            (value, f'Если не указано: {label}') for value, label in WordForm.PART_OF_SPEECH_LABELS.items()
        ]
        self.fields['part_of_speech'].initial = 'noun'
        self.fields['level'].choices = [(c, f'Уровень {c}') for c, _ in Word._meta.get_field('level').choices]


class NewPasswordForm(SetPasswordForm):
    """Setting a password from a reset link, styled like the other forms."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({'class': INPUT, 'placeholder': 'Новый пароль', 'autofocus': True})
        self.fields['new_password2'].widget.attrs.update({'class': INPUT, 'placeholder': 'Повторите пароль'})


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
    deck = forms.ModelChoiceField(queryset=Deck.objects.none(), empty_label=None, widget=forms.Select(attrs={'class': INPUT}))

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

    def __init__(self, *args, decks, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['deck'].queryset = decks
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


class ClubSessionForm(forms.ModelForm):
    """A talking club session; the time is typed in the club's time zone (teach_views)."""

    class Meta:
        model = ClubSession
        fields = ['title', 'starts_at', 'duration_minutes', 'place', 'seats']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Например: Small talk о путешествиях', 'autofocus': True}),
            'starts_at': forms.DateTimeInput(attrs={'class': INPUT, 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'duration_minutes': forms.NumberInput(attrs={'class': INPUT, 'min': 15, 'max': 600, 'step': 5}),
            'place': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Адрес кафе или ссылка на Zoom'}),
            'seats': forms.NumberInput(attrs={'class': INPUT, 'min': 1, 'max': 500}),
        }

    def clean_starts_at(self):
        starts_at = self.cleaned_data['starts_at']
        changed = self.instance.pk is None or 'starts_at' in self.changed_data
        if changed and starts_at <= timezone.now():
            raise forms.ValidationError('Сеанс должен начинаться в будущем.')
        return starts_at

    def clean_seats(self):
        seats = self.cleaned_data['seats']
        taken = self.instance.taken() if self.instance.pk else 0
        if seats < max(taken, 1):
            raise forms.ValidationError(f'Мест не может быть меньше, чем уже записано ({taken}).')
        return seats




class InstagramBotForm(forms.ModelForm):
    """Keys from the teacher's own Meta app (/teach/bot/). Saved ones stay when left empty."""

    SECRETS = ['app_secret', 'access_token']

    class Meta:
        model = InstagramBot
        fields = ['app_secret', 'access_token']
        widgets = {
            'app_secret': forms.PasswordInput(attrs={'class': INPUT, 'autocomplete': 'off'}),
            'access_token': forms.PasswordInput(attrs={'class': INPUT, 'autocomplete': 'off', 'placeholder': 'IGAA…'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.SECRETS:
            self.fields[name].required = not getattr(self.instance, name)
            if getattr(self.instance, name):
                self.fields[name].widget.attrs['placeholder'] = 'Сохранён — оставьте пустым, чтобы не менять'

    def clean(self):
        cleaned = super().clean()
        for name in self.SECRETS:
            cleaned[name] = (cleaned.get(name) or '').strip() or getattr(self.instance, name)
        return cleaned

    def save(self, commit=True):
        account = super().save(commit=False)
        for name in self.SECRETS:
            setattr(account, name, self.cleaned_data[name])
        if commit:
            account.save()
        return account


class PaymentQRForm(forms.Form):
    """A bank QR the bot sends after a booking; cleaned `image` is (bytes, content type)."""

    TYPES = {b'\xff\xd8\xff': 'image/jpeg', b'\x89PNG': 'image/png', b'RIFF': 'image/webp'}
    MAX_BYTES = 2 * 1024 * 1024

    image = forms.FileField(required=False, widget=forms.FileInput(attrs={
        'class': INPUT, 'accept': 'image/jpeg,image/png,image/webp',
    }))
    remove = forms.BooleanField(required=False)

    def clean_image(self):
        upload = self.cleaned_data.get('image')
        if not upload:
            return None
        if upload.size > self.MAX_BYTES:
            raise forms.ValidationError('Картинка больше 2 МБ.')
        data = upload.read()
        content_type = next((t for magic, t in self.TYPES.items() if data.startswith(magic)), None)
        if content_type is None:
            raise forms.ValidationError('Нужна картинка JPEG, PNG или WebP.')
        return data, content_type


class SiteSettingsForm(forms.ModelForm):
    """«Админка → Настройки». Empty fields fall back to .env, shown as placeholders."""

    class Meta:
        model = SiteSettings
        fields = ['club_time_zone', 'google_oauth_client_id']
        widgets = {'google_oauth_client_id': forms.TextInput(attrs={'class': INPUT})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['club_time_zone'].widget = forms.Select(
            attrs={'class': INPUT},
            choices=[('', f'Из .env: {settings.CLUB_TIME_ZONE}')] + [(z, z) for z in sorted(zoneinfo.available_timezones())],
        )
        if settings.GOOGLE_OAUTH_CLIENT_ID:
            self.fields['google_oauth_client_id'].widget.attrs['placeholder'] = f'Из .env: {settings.GOOGLE_OAUTH_CLIENT_ID}'

    def clean_club_time_zone(self):
        zone = self.cleaned_data['club_time_zone']
        if zone and zone not in zoneinfo.available_timezones():
            raise forms.ValidationError('Неизвестный часовой пояс.')
        return zone
