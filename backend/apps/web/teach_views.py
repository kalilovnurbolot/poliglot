"""Teacher's page (/teach/): talking club sessions, the Instagram bot, QR tickets."""

import io
from functools import wraps

import segno
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.club import bot, instagram
from apps.club.models import Booking, ClubSession, InstagramBot
from apps.users.activity import Action, log_activity

from .forms import ClubSessionForm, InstagramBotForm, PaymentQRForm

PAST_SESSIONS = 10


def teacher_required(view):
    """Teachers only; times on these pages are typed and shown in the club's time zone."""
    @login_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.can_teach:
            return render(request, 'web/staff_only.html', {
                'message': 'Этот раздел для учителей. Роль учителя назначает администратор.',
            }, status=403)
        with timezone.override(bot.club_tz()):
            return view(request, *args, **kwargs)
    return wrapper


def _site_url(request):
    return request.build_absolute_uri('/')


def _sessions(teacher):
    return ClubSession.objects.filter(teacher=teacher).annotate(
        taken_count=Count('bookings', filter=Q(bookings__status__in=Booking.ACTIVE), distinct=True),
        waiting_count=Count('waitlist', distinct=True),
    )


def _own_session(request, pk):
    return get_object_or_404(ClubSession, pk=pk, teacher=request.user)


@teacher_required
def teach(request):
    now = timezone.now()
    return render(request, 'web/teach.html', {
        'upcoming': _sessions(request.user).filter(starts_at__gt=now),
        'past': _sessions(request.user).filter(starts_at__lte=now).order_by('-starts_at')[:PAST_SESSIONS],
        'bot': InstagramBot.objects.filter(teacher=request.user).first(),
    })


@teacher_required
def session_create(request):
    form = ClubSessionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        session = form.save(commit=False)
        session.teacher = request.user
        session.save()
        log_activity(request, Action.CLUB_SESSION_CREATE, session.title)
        messages.success(request, 'Сеанс запланирован. Клиенты увидят его в боте.')
        return redirect('web:teach-session', pk=session.pk)
    return render(request, 'web/teach_session_form.html', {
        'form': form, 'title': 'Новый сеанс', 'submit_label': 'Запланировать',
        'back_url': reverse('web:teach'),
    })


@teacher_required
def session_edit(request, pk):
    session = _own_session(request, pk)
    old_when, old_place, old_seats = session.starts_at, session.place, session.seats
    form = ClubSessionForm(request.POST or None, instance=session)
    if request.method == 'POST' and form.is_valid():
        session = form.save()
        if session.starts_at != old_when or session.place != old_place:
            place = f'\n📍 {session.place}' if session.place else ''
            bot.tell_booked(session, f'Сеанс «{session.title}» изменился: теперь {bot.when(session.starts_at)}.{place}')
        if session.seats > old_seats:
            bot.notify_waitlist(session, _site_url(request))
        messages.success(request, 'Сеанс сохранён.')
        return redirect('web:teach-session', pk=session.pk)
    return render(request, 'web/teach_session_form.html', {
        'form': form, 'title': 'Изменить сеанс', 'submit_label': 'Сохранить',
        'back_url': reverse('web:teach-session', args=[session.pk]),
    })


@teacher_required
def session_detail(request, pk):
    session = _own_session(request, pk)
    bookings = session.bookings.select_related('client').order_by('status', 'created_at')
    return render(request, 'web/teach_session.html', {
        'session': session,
        'active': [b for b in bookings if b.is_active],
        'cancelled': [b for b in bookings if not b.is_active],
        'waitlist': session.waitlist.select_related('client'),
        'taken': session.taken(),
    })


@teacher_required
@require_POST
def session_delete(request, pk):
    session = _own_session(request, pk)
    if session.is_upcoming:
        bot.tell_booked(session, f'Сеанс «{session.title}» ({bot.when(session.starts_at)}) отменён. Извините!')
    log_activity(request, Action.CLUB_SESSION_DELETE, session.title)
    session.delete()
    messages.success(request, 'Сеанс удалён.')
    return redirect('web:teach')


@teacher_required
@require_POST
def booking_action(request, pk, action):
    booking = get_object_or_404(Booking.objects.select_related('session', 'client__bot'), pk=pk, session__teacher=request.user)
    session = booking.session
    if action == 'attend' and booking.is_active:
        booking.status = Booking.Status.ATTENDED
    elif action == 'unattend' and booking.status == Booking.Status.ATTENDED:
        booking.status = Booking.Status.BOOKED
    elif action == 'cancel' and booking.is_active:
        booking.status = Booking.Status.CANCELLED
    else:
        return redirect('web:teach-session', pk=session.pk)
    booking.save(update_fields=['status', 'updated_at'])
    if action == 'cancel' and session.is_upcoming:
        bot.tell_client(booking.client, f'Учитель отменил вашу запись на «{session.title}» ({bot.when(session.starts_at)}).')
        bot.notify_waitlist(session, _site_url(request))
    return redirect('web:teach-session', pk=session.pk)


def _own_bot(request):
    """The teacher's bot, created on first visit so the webhook URL exists before connecting."""
    account, _ = InstagramBot.objects.get_or_create(teacher=request.user)
    return account


@teacher_required
def bot_settings(request):
    account = _own_bot(request)
    instagram.keep_fresh(account)
    form = InstagramBotForm(request.POST or None, instance=account)
    if request.method == 'POST' and form.is_valid():
        token = form.cleaned_data['access_token']
        try:
            info = instagram.account_info(token)
            account_id = str(info['user_id'])
            if InstagramBot.objects.filter(account_id=account_id).exclude(pk=account.pk).exists():
                raise instagram.InstagramError('этот аккаунт уже подключил другой учитель')
            instagram.subscribe(token)
        except (instagram.InstagramError, KeyError) as e:
            form.add_error('access_token', f'Не получилось подключить: {e}')
        else:
            account = form.save(commit=False)
            account.account_id, account.username = account_id, info.get('username', '')
            account.token_expires_at = timezone.now() + instagram.TOKEN_LIFETIME
            account.connected_at = timezone.now()
            account.save()
            log_activity(request, Action.BOT_CONNECT, f'@{account.username}')
            messages.success(request, f'Бот подключён к @{account.username}. Напишите ему в Direct с другого аккаунта.')
            return redirect('web:teach-bot')
    return render(request, 'web/teach_bot.html', {
        'bot': account,
        'form': form,
        'qr_form': PaymentQRForm(),
        'webhook_url': request.build_absolute_uri(reverse('club:instagram-webhook', args=[account.webhook_key])),
    })


@teacher_required
@require_POST
def bot_payment_qr(request):
    account = _own_bot(request)
    form = PaymentQRForm(request.POST, request.FILES)
    if not form.is_valid():
        for error in form.errors.get('image', []):
            messages.error(request, error)
    elif form.cleaned_data['image']:
        account.payment_qr, account.payment_qr_type = form.cleaned_data['image']
        account.payment_qr_updated_at = timezone.now()
        account.save(update_fields=['payment_qr', 'payment_qr_type', 'payment_qr_updated_at'])
        messages.success(request, 'QR для оплаты сохранён. Бот будет присылать его после записи.')
    elif form.cleaned_data['remove']:
        account.payment_qr, account.payment_qr_type = None, ''
        account.save(update_fields=['payment_qr', 'payment_qr_type'])
        messages.success(request, 'QR для оплаты удалён.')
    return redirect('web:teach-bot')


@teacher_required
@require_POST
def bot_disconnect(request):
    account = _own_bot(request)
    if account.access_token:
        account.access_token = ''
        account.save(update_fields=['access_token'])
        log_activity(request, Action.BOT_DISCONNECT, f'@{account.username}')
        messages.success(request, 'Бот отключён. Записи клиентов сохранились.')
    return redirect('web:teach-bot')


# ---------- QR tickets (public: the link is the ticket) ----------

def ticket(request, token):
    """What the QR code opens: the booking, and for its teacher a check-in button."""
    booking = get_object_or_404(Booking.objects.select_related('session__teacher', 'client'), token=token)
    is_teacher = request.user.is_authenticated and request.user.pk == booking.session.teacher_id
    if request.method == 'POST' and is_teacher and booking.status == Booking.Status.BOOKED:
        booking.status = Booking.Status.ATTENDED
        booking.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'Отмечено: пришёл.')
        return redirect('web:club-ticket', token=token)
    with timezone.override(bot.club_tz()):
        return render(request, 'web/club_ticket.html', {
            'booking': booking, 'session': booking.session, 'is_teacher': is_teacher,
        })


def ticket_qr(request, token):
    """PNG of the ticket's QR code; Instagram fetches it by this URL to show it in Direct."""
    booking = get_object_or_404(Booking, token=token)
    buffer = io.BytesIO()
    segno.make(request.build_absolute_uri(reverse('web:club-ticket', args=[booking.token])), error='m') \
        .save(buffer, kind='png', scale=12, border=3)
    response = HttpResponse(buffer.getvalue(), content_type='image/png')
    response['Cache-Control'] = 'public, max-age=86400'
    return response


def payment_qr(request, pk):
    """A teacher's payment QR; Instagram fetches it by this URL to show it in Direct."""
    account = get_object_or_404(InstagramBot, pk=pk)
    if not account.payment_qr:
        raise Http404
    response = HttpResponse(bytes(account.payment_qr), content_type=account.payment_qr_type)
    response['Cache-Control'] = 'public, max-age=86400'
    return response
