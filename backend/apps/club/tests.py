import hashlib
import hmac
import json
from datetime import timedelta
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.core.models import SiteSettings
from apps.users.models import User

from . import bot
from .models import Booking, ClubSession, Client, InstagramBot, WaitlistEntry

SECRET = 'app-secret'
PNG = b'\x89PNG\r\n\x1a\nfake'
STATIC = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}


@override_settings(STORAGES=STATIC)
class BotTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(email='teacher@example.com', password='pass12345!x', is_teacher=True)
        self.account = InstagramBot.objects.create(
            teacher=self.teacher, account_id='1000', username='club', access_token='t', app_secret=SECRET,
        )
        self.url = f'/club/instagram/webhook/{self.account.webhook_key}/'
        self.session = ClubSession.objects.create(
            teacher=self.teacher, title='Small talk', starts_at=timezone.now() + timedelta(days=2), seats=1,
        )
        sent = self.sent = []
        patcher = patch('apps.club.instagram.send', side_effect=lambda account, to, message: sent.append((to, message)))
        patcher.start()
        self.addCleanup(patcher.stop)
        patcher = patch('apps.club.instagram.profile', side_effect=lambda account, igsid: f'user{igsid}')
        patcher.start()
        self.addCleanup(patcher.stop)

    def webhook(self, sender, text=None, payload=None):
        message = {'mid': 'm', 'text': text or payload}
        if payload:
            message['quick_reply'] = {'payload': payload}
        body = json.dumps({'object': 'instagram', 'entry': [{
            'id': '1000', 'messaging': [{'sender': {'id': sender}, 'recipient': {'id': '1000'}, 'message': message}],
        }]}).encode()
        signature = 'sha256=' + hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()
        self.sent.clear()
        response = self.client.post(self.url, body, content_type='application/json',
                                    headers={'X-Hub-Signature-256': signature})
        self.assertEqual(response.status_code, 200)
        return self.sent

    def buttons(self, message):
        return [q['payload'] for q in message.get('quick_replies', [])]

    def test_webhook_verification_and_signature(self):
        self.assertEqual(self.client.get(self.url, {'hub.mode': 'subscribe', 'hub.verify_token': 'x'}).status_code, 403)
        response = self.client.get(self.url, {
            'hub.mode': 'subscribe', 'hub.verify_token': self.account.verify_token, 'hub.challenge': '42',
        })
        self.assertEqual(response.content, b'42')
        self.account.refresh_from_db()
        self.assertIsNotNone(self.account.webhook_verified_at)

        # Signed with another teacher's secret, or not at all.
        response = self.client.post(self.url, b'{}', content_type='application/json',
                                    headers={'X-Hub-Signature-256': 'sha256=bad'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.client.get('/club/instagram/webhook/unknown/').status_code, 404)

        self.webhook('A', text='hi')
        self.account.refresh_from_db()
        self.assertIsNotNone(self.account.last_event_at)

    def test_booking_waitlist_and_freed_seat(self):
        # First message: the list of sessions with a button each.
        [(to, message)] = self.webhook('A', text='Привет')
        self.assertEqual(to, 'A')
        self.assertIn('Small talk', message['text'])
        self.assertEqual(self.buttons(message), [f'PICK:{self.session.pk}'])
        self.assertEqual(Client.objects.get(instagram_id='A').username, 'userA')

        # Picking it: the QR ticket with the details, then the payment QR with the buttons.
        self.account.payment_qr, self.account.payment_qr_type = PNG, 'image/png'
        self.account.payment_qr_updated_at = timezone.now()
        self.account.save()
        image, details, payment_image, payment = self.webhook('A', payload=f'PICK:{self.session.pk}')
        booking = Booking.objects.get(client__instagram_id='A')
        self.assertTrue(image[1]['attachment']['payload']['url'].endswith(f'/club/ticket/{booking.token}/qr.png'))
        self.assertIn('Готово, вы записаны', details[1]['text'])
        payment_url = payment_image[1]['attachment']['payload']['url']
        self.assertIn(f'/club/payment-qr/{self.account.pk}/?v=', payment_url)
        self.assertEqual(self.client.get(payment_url.removeprefix('http://testserver')).content, PNG)
        self.assertIn('Оплата', payment[1]['text'])
        self.assertIn('CANCEL', self.buttons(payment[1]))

        # Asking for the ticket again doesn't repeat the payment.
        image, details = self.webhook('A', text='билет')
        self.assertIn('CANCEL', self.buttons(details[1]))

        # Any later message is about that session.
        [(_, message)] = self.webhook('A', text='а когда?')
        self.assertIn('Вы записаны', message['text'])

        # The only seat is taken: B is offered a notification instead.
        self.webhook('B', text='hi')
        [(_, message)] = self.webhook('B', payload=f'PICK:{self.session.pk}')
        self.assertIn('мест не осталось', message['text'])
        self.assertIn(f'NOTIFY:{self.session.pk}', self.buttons(message))
        self.webhook('B', payload=f'NOTIFY:{self.session.pk}')
        self.assertTrue(WaitlistEntry.objects.filter(client__instagram_id='B', notified_at=None).exists())
        [(_, message)] = self.webhook('B', text='?')
        self.assertIn('листе ожидания', message['text'])

        # A cancels by typing: B hears about the seat and books it.
        sent = self.webhook('A', text='Отменить')
        self.assertEqual([to for to, _ in sent], ['A', 'B'])
        self.assertIn('Освободилось место', sent[1][1]['text'])
        self.assertEqual(Booking.objects.get(client__instagram_id='A').status, Booking.Status.CANCELLED)
        self.webhook('B', payload=f'PICK:{self.session.pk}')
        self.assertTrue(Booking.objects.filter(client__instagram_id='B', status=Booking.Status.BOOKED).exists())
        self.assertFalse(WaitlistEntry.objects.exists())

        # A asks for the ticket after cancelling: nothing to show, so the list again.
        sent = self.webhook('A', text='билет')
        self.assertIn('нет записи', sent[0][1]['text'])

    def test_past_sessions_are_not_offered(self):
        self.session.starts_at = timezone.now() - timedelta(hours=1)
        self.session.save()
        [(_, message)] = self.webhook('A', text='hi')
        self.assertIn('Пока нет', message['text'])
        [(_, message), _] = self.webhook('A', payload=f'PICK:{self.session.pk}')
        self.assertIn('недоступен', message['text'])

    def test_echoes_and_inactive_bots_are_ignored(self):
        self.webhook('1000', text='echo of our own message')
        self.account.access_token = ''
        self.account.save()
        self.assertEqual(self.webhook('A', text='hi'), [])

    def test_teacher_pages(self):
        student = User.objects.create_user(email='s@example.com', password='pass12345!x')
        self.client.force_login(student)
        self.assertEqual(self.client.get('/teach/').status_code, 403)

        self.client.force_login(self.teacher)
        self.assertContains(self.client.get('/teach/'), 'Small talk')
        self.assertContains(self.client.get('/teach/'), 'Добавить видео')
        starts = timezone.localtime(timezone.now() + timedelta(days=3), bot.club_tz())
        response = self.client.post('/teach/sessions/new/', {
            'title': 'Movies', 'starts_at': starts.strftime('%Y-%m-%dT%H:%M'),
            'duration_minutes': 90, 'place': 'Cafe', 'seats': 5,
        })
        created = ClubSession.objects.get(title='Movies')
        self.assertRedirects(response, f'/teach/sessions/{created.pk}/')
        # Typed in the club's zone, stored as the same moment.
        self.assertEqual(timezone.localtime(created.starts_at, bot.club_tz()).hour, starts.hour)
        response = self.client.post('/teach/sessions/new/', {
            'title': 'Old', 'starts_at': '2020-01-01T10:00', 'duration_minutes': 60, 'seats': 5,
        })
        self.assertContains(response, 'в будущем')

        # Another teacher's session is out of reach.
        other = User.objects.create_user(email='o@example.com', password='pass12345!x', is_teacher=True)
        self.client.force_login(other)
        self.assertEqual(self.client.get(f'/teach/sessions/{self.session.pk}/').status_code, 404)

    def test_teacher_cancels_booking_and_adds_seats(self):
        a = Client.objects.create(bot=self.account, instagram_id='A')
        b = Client.objects.create(bot=self.account, instagram_id='B')
        booking = Booking.objects.create(session=self.session, client=a)
        WaitlistEntry.objects.create(session=self.session, client=b)
        self.client.force_login(self.teacher)

        response = self.client.post(f'/teach/sessions/{self.session.pk}/edit/', {
            'title': 'Small talk', 'starts_at': timezone.localtime(self.session.starts_at, bot.club_tz()).strftime('%Y-%m-%dT%H:%M'),
            'duration_minutes': 60, 'place': '', 'seats': 0,
        })
        self.assertContains(response, 'меньше')

        self.client.post(f'/teach/bookings/{booking.pk}/cancel/')
        self.assertEqual([to for to, _ in self.sent], ['A', 'B'])
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.CANCELLED)

    def test_ticket_and_check_in(self):
        a = Client.objects.create(bot=self.account, instagram_id='A', username='anna')
        booking = Booking.objects.create(session=self.session, client=a)
        response = self.client.get(f'/club/ticket/{booking.token}/qr.png')
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertTrue(response.content.startswith(b'\x89PNG'))

        page = self.client.get(f'/club/ticket/{booking.token}/')
        self.assertContains(page, '@anna')
        self.assertNotContains(page, 'Отметить: пришёл')
        self.client.post(f'/club/ticket/{booking.token}/')
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.BOOKED)

        self.client.force_login(self.teacher)
        self.assertContains(self.client.get(f'/club/ticket/{booking.token}/'), 'Отметить: пришёл')
        self.client.post(f'/club/ticket/{booking.token}/')
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.ATTENDED)

    @patch('apps.club.instagram.subscribe')
    @patch('apps.club.instagram.account_info', return_value={'user_id': '2000', 'username': 'newclub'})
    def test_teacher_sets_up_own_bot(self, account_info, subscribe):
        teacher = User.objects.create_user(email='new@example.com', password='pass12345!x', is_teacher=True)
        self.client.force_login(teacher)

        # The first visit makes the personal webhook URL and verify token to paste into Meta.
        page = self.client.get('/teach/bot/')
        account = InstagramBot.objects.get(teacher=teacher)
        self.assertContains(page, f'http://testserver/club/instagram/webhook/{account.webhook_key}/')
        self.assertContains(page, account.verify_token)
        self.assertNotEqual(account.webhook_key, self.account.webhook_key)
        self.assertEqual(self.client.get('/teach/bot/').context['bot'].webhook_key, account.webhook_key)

        self.assertContains(self.client.post('/teach/bot/', {'app_secret': '', 'access_token': ''}), 'Обязательное поле')
        response = self.client.post('/teach/bot/', {'app_secret': 'mysecret', 'access_token': 'IGAAnew'})
        self.assertRedirects(response, '/teach/bot/')
        subscribe.assert_called_once_with('IGAAnew')
        account.refresh_from_db()
        self.assertEqual((account.account_id, account.username, account.app_secret, account.access_token),
                         ('2000', 'newclub', 'mysecret', 'IGAAnew'))
        self.assertTrue(account.is_active)
        page = self.client.get('/teach/bot/')
        self.assertContains(page, '@newclub')
        self.assertNotContains(page, 'mysecret')

        # Saving again with empty fields keeps the keys.
        self.client.post('/teach/bot/', {'app_secret': '', 'access_token': ''})
        account.refresh_from_db()
        self.assertEqual(account.app_secret, 'mysecret')

        # The payment QR is the teacher's own.
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.post('/teach/bot/payment-qr/', {'image': SimpleUploadedFile('qr.png', PNG)})
        self.assertEqual(self.client.get(f'/club/payment-qr/{account.pk}/').content, PNG)
        self.client.post('/teach/bot/payment-qr/', {'image': SimpleUploadedFile('qr.txt', b'hello')}, follow=True)
        self.assertContains(self.client.get('/teach/bot/'), 'QR для оплаты')
        self.client.post('/teach/bot/payment-qr/', {'remove': 'on'})
        self.assertEqual(self.client.get(f'/club/payment-qr/{account.pk}/').status_code, 404)

        self.client.post('/teach/bot/disconnect/')
        account.refresh_from_db()
        self.assertFalse(account.is_active)

        # Someone else's account can't be taken over.
        account_info.return_value = {'user_id': '1000', 'username': 'club'}
        response = self.client.post('/teach/bot/', {'app_secret': 'x', 'access_token': 'y'})
        self.assertContains(response, 'другой учитель')

    @patch('apps.club.instagram.refresh', return_value=('IGAAfresh', timezone.now() + timedelta(days=60)))
    def test_tokens_are_refreshed_before_expiry(self, refresh):
        self.account.token_expires_at = timezone.now() + timedelta(days=40)
        self.account.save()
        call_command('refresh_instagram_tokens')
        refresh.assert_not_called()
        self.account.token_expires_at = timezone.now() + timedelta(days=10)
        self.account.save()
        call_command('refresh_instagram_tokens')
        self.account.refresh_from_db()
        self.assertEqual(self.account.access_token, 'IGAAfresh')


class WordsTests(TestCase):
    def test_seats_word(self):
        self.assertEqual([bot.seats_word(n) for n in (1, 2, 5, 11, 21, 22)],
                         ['1 место', '2 места', '5 мест', '11 мест', '21 место', '22 места'])


@override_settings(STORAGES=STATIC)
class SiteSettingsTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='kalilovnurbolot3@gmail.com', password='pass12345!x')
        self.admin = User.objects.create_user(email='admin@example.com', password='pass12345!x', is_staff=True)

    def test_only_owners(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get('/manage/settings/').status_code, 403)

    def test_time_zone(self):
        self.client.force_login(self.owner)
        self.client.post('/manage/settings/', {'club_time_zone': 'Europe/Berlin', 'google_oauth_client_id': ''})
        self.assertEqual(bot.club_tz().key, 'Europe/Berlin')
        response = self.client.post('/manage/settings/', {'club_time_zone': 'Mars/Base', 'google_oauth_client_id': ''})
        self.assertContains(response, 'Неизвестный часовой пояс')
        self.client.post('/manage/settings/', {'club_time_zone': '', 'google_oauth_client_id': ''})
        self.assertEqual(bot.club_tz().key, 'Asia/Bishkek')

    def test_env_is_the_fallback(self):
        from apps.core.models import site_setting
        with self.settings(GOOGLE_OAUTH_CLIENT_ID='from-env'):
            self.assertEqual(site_setting('google_oauth_client_id'), 'from-env')
            SiteSettings.objects.create(pk=1, google_oauth_client_id='from-admin')
            self.assertEqual(site_setting('google_oauth_client_id'), 'from-admin')
