import secrets
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


def new_token():
    return secrets.token_urlsafe(16)


class InstagramBot(models.Model):
    """A teacher's own Instagram bot: their Meta app talks to the site through a personal webhook.

    The row appears when the teacher first opens /teach/bot/, so the webhook URL and verify
    token to paste into their app exist before anything is connected. Disconnecting only
    clears the token: clients and their bookings stay.
    """

    teacher = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='instagram_bot')
    # In the webhook URL (/club/instagram/webhook/<key>/), so events find their bot.
    webhook_key = models.CharField(max_length=32, unique=True, default=new_token)
    verify_token = models.CharField(max_length=32, default=new_token)
    # «Instagram app secret» of the teacher's Meta app: signs the webhook events.
    app_secret = models.CharField(max_length=128, blank=True)
    access_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    # The Instagram account the token belongs to (`entry.id` in webhook events).
    account_id = models.CharField(max_length=64, unique=True, null=True, blank=True)
    username = models.CharField(max_length=64, blank=True)
    connected_at = models.DateTimeField(null=True, blank=True)
    # What the teacher's page shows to tell them the Meta side is set up right.
    webhook_verified_at = models.DateTimeField(null=True, blank=True)
    last_event_at = models.DateTimeField(null=True, blank=True)
    # Sent after a booking: the teacher's own bank QR.
    payment_qr = models.BinaryField(null=True, blank=True)
    payment_qr_type = models.CharField(max_length=32, blank=True)
    payment_qr_updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'@{self.username}' if self.username else f'бот {self.teacher}'

    @property
    def is_active(self):
        return bool(self.access_token and self.app_secret)


class ClubSession(models.Model):
    """A talking club meeting planned by a teacher; clients book a seat through the bot."""

    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='club_sessions')
    title = models.CharField('Тема', max_length=120)
    starts_at = models.DateTimeField('Начало')
    duration_minutes = models.PositiveSmallIntegerField('Длительность, мин', default=60)
    place = models.CharField('Место или ссылка', max_length=200, blank=True)
    seats = models.PositiveSmallIntegerField('Мест', default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['starts_at']

    def __str__(self):
        return f'{self.title} ({self.starts_at:%Y-%m-%d %H:%M})'

    @property
    def ends_at(self):
        return self.starts_at + timedelta(minutes=self.duration_minutes)

    @property
    def is_upcoming(self):
        return self.starts_at > timezone.now()

    def taken(self):
        return self.bookings.filter(status__in=Booking.ACTIVE).count()

    def seats_left(self):
        return max(self.seats - self.taken(), 0)


class Client(models.Model):
    """Someone who wrote to a teacher's bot, known by their Instagram-scoped id."""

    bot = models.ForeignKey(InstagramBot, on_delete=models.CASCADE, related_name='clients')
    instagram_id = models.CharField(max_length=64)
    username = models.CharField(max_length=64, blank=True)
    # The session the conversation is about since the client picked it (bot.py).
    current_session = models.ForeignKey(ClubSession, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['bot', 'instagram_id'], name='club_client_unique')]

    def __str__(self):
        return f'@{self.username}' if self.username else f'id {self.instagram_id}'


class Booking(models.Model):
    """A client's seat at a session; `token` is what their QR ticket encodes."""

    class Status(models.TextChoices):
        BOOKED = 'booked', 'Записан'
        ATTENDED = 'attended', 'Пришёл'
        CANCELLED = 'cancelled', 'Отменена'

    ACTIVE = [Status.BOOKED, Status.ATTENDED]

    session = models.ForeignKey(ClubSession, on_delete=models.CASCADE, related_name='bookings')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='bookings')
    token = models.CharField(max_length=32, unique=True, default=new_token)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.BOOKED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        constraints = [models.UniqueConstraint(fields=['session', 'client'], name='club_booking_unique')]

    def __str__(self):
        return f'{self.client} → {self.session}'

    @property
    def is_active(self):
        return self.status in self.ACTIVE


class WaitlistEntry(models.Model):
    """A client waiting for a seat at a full session; notified once when one frees up."""

    session = models.ForeignKey(ClubSession, on_delete=models.CASCADE, related_name='waitlist')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='waitlist')
    created_at = models.DateTimeField(auto_now_add=True)
    notified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['created_at']
        constraints = [models.UniqueConstraint(fields=['session', 'client'], name='club_waitlist_unique')]

    def __str__(self):
        return f'{self.client} ждёт {self.session}'
