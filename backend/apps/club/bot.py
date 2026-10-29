"""The teacher's Instagram bot: clients book talking club sessions in Direct.

The first message gets the list of upcoming sessions. Picking one ties the conversation to
it (Client.current_session): a booking with a QR ticket, or, when the seats are gone, an
offer to be told when one frees up. From then on the bot talks about that session — the
ticket again, cancelling — until the client asks for the list again.

Commands arrive as quick-reply payloads ("PICK:12") or as typed words (COMMAND_WORDS).
"""

import logging
import zoneinfo

from django.db import transaction
from django.db.models import Count, Q
from django.urls import reverse
from django.utils import timezone

from apps.core.models import site_setting

from . import instagram
from .models import Booking, ClubSession, Client, WaitlistEntry

logger = logging.getLogger(__name__)

MAX_SESSIONS = 10
WEEKDAYS = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']

# Typed words that work like the buttons.
COMMAND_WORDS = {
    'SESSIONS': {'сеансы', 'расписание', 'записаться', 'запись', 'меню', 'start', 'sessions'},
    'TICKET': {'билет', 'qr', 'код', 'qr-код'},
    'CANCEL': {'отмена', 'отменить', 'cancel'},
}
MORE_SESSIONS = ('Другие сеансы', 'SESSIONS')


def club_tz():
    return zoneinfo.ZoneInfo(site_setting('club_time_zone'))


def when(dt):
    """'пт 31.10, 19:00' in the club's time zone."""
    local = timezone.localtime(dt, club_tz())
    return f'{WEEKDAYS[local.weekday()]} {local:%d.%m, %H:%M}'


def seats_word(n):
    if n % 10 == 1 and n % 100 != 11:
        return f'{n} место'
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return f'{n} места'
    return f'{n} мест'


def upcoming_sessions(teacher):
    return ClubSession.objects.filter(teacher=teacher, starts_at__gt=timezone.now()).annotate(
        taken_count=Count('bookings', filter=Q(bookings__status__in=Booking.ACTIVE), distinct=True),
    )


def parse(text):
    """('PICK', '12') from a payload, ('TICKET', '') from a typed «билет», ('', '') otherwise."""
    text = (text or '').strip()
    command, _, arg = text.partition(':')
    if command in ('SESSIONS', 'PICK', 'NOTIFY', 'TICKET', 'CANCEL'):
        return command, arg
    word = text.lower().strip('/!. ')
    for command, words in COMMAND_WORDS.items():
        if word in words:
            return command, ''
    return '', ''


class Conversation:
    """One incoming message from a client and the bot's answers to it."""

    def __init__(self, bot, client, site_url):
        self.bot = bot
        self.client = client
        self.site_url = site_url.rstrip('/')

    def say(self, text, buttons=()):
        instagram.send_text(self.bot, self.client.instagram_id, text, buttons)

    def handle(self, text):
        command, arg = parse(text)
        if command == 'PICK':
            self.pick(arg)
        elif command == 'NOTIFY':
            self.notify_me(arg)
        elif command == 'TICKET':
            self.ticket()
        elif command == 'CANCEL':
            self.cancel()
        elif command == 'SESSIONS' or not self.current_session():
            self.sessions()
        else:
            self.session_menu()

    # ---------- What the client is talking about ----------

    def current_session(self):
        session = self.client.current_session
        if session is None or session.teacher_id != self.bot.teacher_id or not session.is_upcoming:
            return None
        return session

    def booking(self, session):
        return Booking.objects.filter(session=session, client=self.client, status__in=Booking.ACTIVE).first()

    def find_session(self, arg):
        if not arg.isdigit():
            return None
        return upcoming_sessions(self.bot.teacher).filter(pk=int(arg)).first()

    # ---------- Commands ----------

    def sessions(self):
        found = list(upcoming_sessions(self.bot.teacher)[:MAX_SESSIONS])
        if not found:
            self.say('Пока нет запланированных сеансов разговорного клуба. Загляните позже 🙂')
            return
        lines = ['Ближайшие сеансы разговорного клуба:', '']
        buttons = []
        for number, session in enumerate(found, 1):
            left = max(session.seats - session.taken_count, 0)
            lines.append(f'{number}. {session.title} — {when(session.starts_at)} '
                         f'({seats_word(left) if left else "мест нет"})')
            local = timezone.localtime(session.starts_at, club_tz())
            buttons.append((f'{number} · {local:%d.%m %H:%M}', f'PICK:{session.pk}'))
        lines += ['', 'Выберите сеанс кнопкой ниже.']
        self.say('\n'.join(lines), buttons)

    def pick(self, arg):
        session = self.find_session(arg)
        if session is None:
            self.say('Этот сеанс уже недоступен.')
            self.sessions()
            return
        self.client.current_session = session
        self.client.save(update_fields=['current_session'])

        with transaction.atomic():
            # Locking the session makes two clients racing for the last seat take turns.
            session = ClubSession.objects.select_for_update().get(pk=session.pk)
            booking = Booking.objects.filter(session=session, client=self.client).first()
            already = booking is not None and booking.is_active
            if not already:
                if session.seats_left() == 0:
                    booking = None
                elif booking is None:
                    booking = Booking.objects.create(session=session, client=self.client)
                else:
                    booking.status = Booking.Status.BOOKED
                    booking.save(update_fields=['status', 'updated_at'])
            if booking is not None:
                WaitlistEntry.objects.filter(session=session, client=self.client).delete()

        if booking is None:
            self.say(
                f'На «{session.title}» ({when(session.starts_at)}) мест не осталось 😔\n'
                'Хотите, напишу, как только освободится место?',
                [('🔔 Уведомить', f'NOTIFY:{session.pk}'), MORE_SESSIONS],
            )
            return
        self.send_ticket(booking, 'Вы уже записаны' if already else 'Готово, вы записаны', payment=True)

    def notify_me(self, arg):
        session = self.find_session(arg)
        if session is None:
            self.say('Этот сеанс уже недоступен.')
            self.sessions()
            return
        if session.seats_left() > 0:
            self.pick(arg)
            return
        self.client.current_session = session
        self.client.save(update_fields=['current_session'])
        entry, created = WaitlistEntry.objects.get_or_create(session=session, client=self.client)
        if not created and entry.notified_at:
            entry.notified_at = None
            entry.save(update_fields=['notified_at'])
        self.say(f'Хорошо! Напишу, как только на «{session.title}» ({when(session.starts_at)}) '
                 'освободится место.', [MORE_SESSIONS])

    def ticket(self):
        session = self.current_session()
        booking = self.booking(session) if session else None
        if booking is None:
            # Not about a booked session right now: the nearest booking, if any.
            booking = Booking.objects.filter(
                client=self.client, status__in=Booking.ACTIVE, session__starts_at__gt=timezone.now(),
            ).select_related('session').order_by('session__starts_at').first()
        if booking is None:
            self.say('У вас пока нет записи на сеанс.')
            self.sessions()
            return
        self.send_ticket(booking, 'Ваш билет')

    def cancel(self):
        session = self.current_session()
        booking = self.booking(session) if session else None
        if booking is None:
            self.say('Отменять нечего: записи на этот сеанс нет.', [MORE_SESSIONS])
            return
        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=['status', 'updated_at'])
        self.say(f'Запись на «{session.title}» ({when(session.starts_at)}) отменена.', [MORE_SESSIONS])
        notify_waitlist(session, self.site_url)

    def session_menu(self):
        session = self.current_session()
        if self.booking(session):
            self.say(f'Вы записаны на «{session.title}» — {when(session.starts_at)}.',
                     [('Мой QR-код', 'TICKET'), ('Отменить запись', 'CANCEL'), MORE_SESSIONS])
        elif WaitlistEntry.objects.filter(session=session, client=self.client).exists():
            self.say(f'Вы в листе ожидания на «{session.title}» — {when(session.starts_at)}. '
                     'Напишу, когда освободится место.',
                     [('Проверить места', f'PICK:{session.pk}'), MORE_SESSIONS])
        else:
            self.sessions()

    def send_ticket(self, booking, heading, payment=False):
        session = booking.session
        qr_url = self.site_url + reverse('web:club-ticket-qr', args=[booking.token])
        instagram.send_image(self.bot, self.client.instagram_id, qr_url)
        lines = [f'{heading}: «{session.title}»', f'🗓 {when(session.starts_at)}, {session.duration_minutes} мин']
        if session.place:
            lines.append(f'📍 {session.place}')
        lines += ['', 'Покажите этот QR-код учителю на входе.']
        buttons = [('Отменить запись', 'CANCEL'), MORE_SESSIONS]
        if not (payment and self.bot.payment_qr):
            self.say('\n'.join(lines), buttons)
            return
        # The teacher's bank QR (/teach/bot/); buttons go under the last message.
        self.say('\n'.join(lines))
        qr_url = reverse('web:club-payment-qr', args=[self.bot.pk]) \
            + f'?v={int(self.bot.payment_qr_updated_at.timestamp())}'
        instagram.send_image(self.bot, self.client.instagram_id, self.site_url + qr_url)
        self.say('💳 Оплата участия: отсканируйте QR-код выше в приложении банка.', buttons)


def handle_event(bot, event, site_url):
    """One item of a webhook entry's `messaging` list: a message or a button tap."""
    message = event.get('message') or {}
    if message.get('is_echo') or message.get('is_deleted'):
        return
    sender = (event.get('sender') or {}).get('id')
    if not sender or sender == bot.account_id:
        return
    text = (message.get('quick_reply') or {}).get('payload') or message.get('text') \
        or (event.get('postback') or {}).get('payload')
    if text is None:
        return  # reactions, read receipts, stickers

    client, created = Client.objects.get_or_create(bot=bot, instagram_id=sender)
    client.last_message_at = timezone.now()
    if created or not client.username:
        client.username = instagram.profile(bot, sender)
    client.save()
    Conversation(bot, client, site_url).handle(text)


def notify_waitlist(session, site_url):
    """A seat freed up: tell everyone waiting; whoever taps first gets it."""
    if not session.is_upcoming or session.seats_left() == 0:
        return
    waiting = WaitlistEntry.objects.filter(session=session, notified_at__isnull=True).select_related('client__bot')
    for entry in waiting:
        if not entry.client.bot.is_active:
            continue
        try:
            instagram.send_text(
                entry.client.bot, entry.client.instagram_id,
                f'Освободилось место на «{session.title}» — {when(session.starts_at)}! Успейте записаться.',
                [('Записаться', f'PICK:{session.pk}'), MORE_SESSIONS],
            )
        except instagram.InstagramError as e:
            # Most often the 24-hour window since the client's last message has closed.
            logger.warning('Waitlist message to %s failed: %s', entry.client, e)
        entry.notified_at = timezone.now()
        entry.save(update_fields=['notified_at'])


def tell_client(client, text):
    """A message from the teacher's side (the session moved, the booking was cancelled)."""
    if not client.bot.is_active:
        return
    try:
        instagram.send_text(client.bot, client.instagram_id, text, [MORE_SESSIONS])
    except instagram.InstagramError as e:
        logger.warning('Message to %s failed: %s', client, e)


def tell_booked(session, text):
    for booking in session.bookings.filter(status=Booking.Status.BOOKED).select_related('client__bot'):
        tell_client(booking.client, text)
