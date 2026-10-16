from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    # Look of the site (apps/web/appearance.py): {"mode", "accent", "tint"}; empty until
    # the user picks something, so new accounts follow the system theme.
    appearance = models.JSONField(default=dict, blank=True)
    appearance_hint_seen = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    @property
    def is_owner(self):
        """Accounts from ADMIN_EMAILS: always admins, and only they manage database versions."""
        return bool(self.email) and self.email.lower() in settings.ADMIN_EMAILS

    def save(self, *args, **kwargs):
        if self.email and self.email.lower() in settings.ADMIN_EMAILS:
            self.is_staff = True
            self.is_superuser = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class ActivityLog(models.Model):
    """Who did what on the site: sign-ins, content changes, admin actions (activity.py)."""

    class Action(models.TextChoices):
        LOGIN = 'login', 'Вход'
        LOGIN_GOOGLE = 'login_google', 'Вход через Google'
        LOGIN_FAILED = 'login_failed', 'Неудачный вход'
        LOGOUT = 'logout', 'Выход'
        REGISTER = 'register', 'Регистрация'
        PASSWORD_RESET = 'password_reset', 'Сменил пароль по ссылке'
        WORD_ADD = 'word_add', 'Добавил слово'
        WORD_DELETE = 'word_delete', 'Удалил слово'
        DECK_CREATE = 'deck_create', 'Создал группу слов'
        GRAMMAR_CREATE = 'grammar_create', 'Создал правило'
        GRAMMAR_EDIT = 'grammar_edit', 'Изменил правило'
        GRAMMAR_DELETE = 'grammar_delete', 'Удалил правило'
        GRAMMAR_LEARNED = 'grammar_learned', 'Отметил правило изученным'
        GRAMMAR_UNLEARNED = 'grammar_unlearned', 'Снял отметку «изучено»'
        ADMIN_GRANT = 'admin_grant', 'Назначил администратором'
        ADMIN_REVOKE = 'admin_revoke', 'Снял права администратора'
        USER_BLOCK = 'user_block', 'Заблокировал пользователя'
        USER_UNBLOCK = 'user_unblock', 'Разблокировал пользователя'
        PASSWORD_LINK = 'password_link', 'Создал ссылку сброса пароля'
        BACKUP_CREATE = 'backup_create', 'Запустил бэкап базы'
        BACKUP_RESTORE = 'backup_restore', 'Запустил восстановление базы'
        BACKUP_DOWNLOAD = 'backup_download', 'Скачал бэкап базы'
        BACKUP_UPLOAD = 'backup_upload', 'Загрузил бэкап базы'

    # The email is kept separately so entries stay readable after a user is deleted.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='activity')
    user_email = models.CharField(max_length=254, blank=True)
    action = models.CharField(max_length=32, choices=Action.choices, db_index=True)
    target = models.CharField(max_length=255, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.created_at:%Y-%m-%d %H:%M} {self.user_email} {self.get_action_display()} {self.target}'
