import hashlib
import hmac
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.core.models import Language
from apps.grammar.models import GrammarProgress, GrammarRule
from apps.users.models import ActivityLog, User
from apps.vocabulary.models import Deck, Word
from apps.vocabulary.queries import default_deck

from .rule_render import extract_lede, extract_sections, render_rule


class RuleRenderTests(TestCase):
    def test_blocks_and_markdown(self):
        body = (
            'Коротко **о главном**.\n\n'
            '## Формы и `код`\n\n'
            '```formula\n+ | [s: I] + [v: am]\n```\n\n'
            '```example\n[s: She] [v: is] ok\n= Она в порядке.\n```\n\n'
            '```note\n× | Не `I amn\'t`\n```\n\n'
            '| a | b |\n|---|---|\n| 1 | 2 |\n\n'
            '<script>alert(1)</script>\n'
        )
        html = render_rule(body)
        self.assertIn('<h2 id="формы-и-код" class="rule-h2">', html)
        self.assertIn('<span class="rule-f-label">+</span><span class="rule-chip rule-chip-s">I</span>', html)
        self.assertIn('<span class="rule-w rule-w-plain">ok</span><span class="rule-tr">Она в порядке.</span>', html)
        self.assertIn('rule-note rule-note-error', html)
        self.assertIn('<code class="rule-mono">I amn&#x27;t</code>', html)
        self.assertIn('<div class="rule-table-wrap"><table>', html)
        self.assertNotIn('<script>', html)

        self.assertEqual(extract_sections(body), [{'id': 'формы-и-код', 'title': 'Формы и код'}])
        self.assertEqual(extract_lede(body), 'Коротко о главном.')


# The real storage needs `collectstatic` to have built its manifest first.
@override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})
class WebPagesTests(TestCase):
    def setUp(self):
        self.en = Language.objects.get(code='en')
        self.user = User.objects.create_user(email='user@example.com', password='pass12345!x')
        self.admin = User.objects.create_user(email='admin@example.com', password='pass12345!x', is_staff=True)

    def test_public_pages(self):
        for url in ['/', '/login/', '/register/', '/grammar/', '/manifest.webmanifest', '/sw.js']:
            self.assertEqual(self.client.get(url).status_code, 200, url)
        rule = GrammarRule.objects.filter(language=self.en).first()
        self.assertContains(self.client.get(f'/grammar/{rule.pk}/'), rule.title)

    def test_private_pages_redirect_to_login(self):
        for url in ['/learn/', '/learn/A1/', '/quiz/', '/words/', '/grammar/new/']:
            res = self.client.get(url)
            self.assertRedirects(res, f'/login/?next={url}', fetch_redirect_response=False)

    def test_register_login_logout(self):
        res = self.client.post('/register/', {'email': 'new@example.com', 'first_name': 'Ая', 'password': 'pass12345!x'})
        self.assertRedirects(res, '/', fetch_redirect_response=False)
        self.assertContains(self.client.get('/'), 'С возвращением, Ая!')

        self.client.post('/logout/')
        res = self.client.post('/login/', {'email': 'new@example.com', 'password': 'wrong'})
        self.assertContains(res, 'Неверный email или пароль')
        res = self.client.post('/login/', {'email': 'new@example.com', 'password': 'pass12345!x', 'next': '/words/'})
        self.assertRedirects(res, '/words/', fetch_redirect_response=False)

    @patch('apps.web.views.user_from_google_token')
    def test_google_login_redirects_to_next(self, verify):
        verify.return_value = self.user
        res = self.client.post('/auth/google/', {'credential': 't', 'next': '/quiz/'}, content_type='application/json')
        self.assertEqual(res.json()['redirect'], '/quiz/')
        res = self.client.post('/auth/google/', {'credential': 't', 'next': 'https://evil.com/'}, content_type='application/json')
        self.assertEqual(res.json()['redirect'], '/')
        res = self.client.post('/auth/google/', {'credential': 't'}, content_type='application/json')
        self.assertEqual(res.json()['redirect'], '/')

    def test_voice_control_only_when_configured(self):
        self.client.force_login(self.user)
        self.assertNotContains(self.client.get('/learn/A1/'), 'id="voice-config"')
        self.assertEqual(self.client.post('/voice/recognize/', b'\0\0', content_type='application/octet-stream').status_code, 404)
        with self.settings(VOICE_SERVICE_URL='ws://voice:2700/'):
            self.assertContains(self.client.get('/learn/A1/'), 'id="voice-config"')

    @override_settings(VOICE_SERVICE_URL='ws://voice:2700/', VOICE_SECRET='s3cret')
    @patch('apps.web.voice.connect')
    def test_voice_recognize(self, connect):
        ws = connect.return_value.__enter__.return_value
        ws.recv.side_effect = ['{"text": "не"}', '{"text": "знаю", "final": true}']
        post = lambda body: self.client.post('/voice/recognize/', body, content_type='application/octet-stream')

        self.assertEqual(post(b'\0\0').status_code, 302)  # login required
        self.client.force_login(self.user)
        self.assertEqual(post(b'\0\0').json(), {'text': 'не знаю'})
        user_id, ts, signature = connect.call_args.args[0].split('token=')[1].split(':')
        expected = hmac.new(b's3cret', f'{user_id}:{ts}'.encode(), hashlib.sha256).hexdigest()
        self.assertEqual((user_id, signature), (str(self.user.pk), expected))

        self.assertEqual(post(b'').status_code, 400)
        self.assertEqual(post(b'\0').status_code, 400)
        self.assertEqual(post(b'\0' * 400_000).status_code, 400)
        connect.side_effect = OSError
        self.assertEqual(post(b'\0\0').status_code, 503)

    def test_appearance_saved_in_account(self):
        post = lambda data: self.client.post('/appearance/', data, content_type='application/json')
        self.assertEqual(post({'hint_seen': True}).status_code, 302)  # login required

        self.client.force_login(self.user)
        page = self.client.get('/').content.decode()
        self.assertIn('id="appearance-data"', page)
        self.assertNotIn('data-theme=', page.split('<head>')[0])

        self.assertEqual(post({'mode': 'dark', 'accent': '#EC4899', 'tint': True}).status_code, 204)
        self.user.refresh_from_db()
        self.assertEqual(self.user.appearance, {'mode': 'dark', 'accent': '#ec4899', 'tint': True})
        self.assertTrue(self.user.appearance_hint_seen)
        html_tag = self.client.get('/').content.decode().split('<head>')[0]
        self.assertIn('data-theme="dark" data-accent style="--accent: #ec4899" data-tint', html_tag)

        for bad in [{'mode': 'pink', 'accent': '', 'tint': False},
                    {'mode': 'light', 'accent': 'red', 'tint': False},
                    {'mode': 'light', 'accent': '#ec4899"><script>', 'tint': False},
                    {'mode': 'light', 'accent': '', 'tint': 'yes'},
                    {}]:
            self.assertEqual(post(bad).status_code, 400, bad)

        other = User.objects.create_user(email='other@example.com', password='pass12345!x')
        self.client.force_login(other)
        self.assertEqual(post({'hint_seen': True}).status_code, 204)
        other.refresh_from_db()
        self.assertEqual((other.appearance, other.appearance_hint_seen), ({}, True))

    def test_learn_and_quiz_pages(self):
        self.client.force_login(self.user)
        topic = Deck.objects.filter(language=self.en, owner=None, words__isnull=False).first()
        for url in ['/learn/', '/quiz/']:
            res = self.client.get(url)
            self.assertContains(res, 'Мои слова')
            self.assertContains(res, topic.name)
        self.assertContains(self.client.get('/learn/A1/'), 'id="cards-data"')
        self.assertContains(self.client.get(f'/learn/group/{topic.pk}/'), 'id="cards-data"')
        self.assertEqual(self.client.get('/learn/Z9/').status_code, 404)
        self.assertContains(self.client.get('/quiz/?level=A1&mode=listening'), 'id="quiz-data"')
        self.assertContains(self.client.get('/quiz/?level=all'), 'id="quiz-data"')
        self.assertContains(self.client.get(f'/quiz/?deck={topic.pk}'), topic.name)
        self.assertEqual(self.client.get('/quiz/?deck=x').status_code, 404)

    def test_own_groups(self):
        self.client.force_login(self.user)
        self.client.post('/words/groups/new/', {'name': ' Работа '})
        work = Deck.objects.get(owner=self.user, name='Работа')
        res = self.client.post('/words/', {
            'text': 'deadline', 'translation': 'срок', 'transcription': '', 'part_of_speech': 'noun',
            'level': 'B1', 'example_sentence': '', 'deck': work.pk,
        })
        self.assertEqual(res.status_code, 302)
        word = Word.objects.get(owner=self.user)
        self.assertEqual(list(word.decks.all()), [work])

        self.assertContains(self.client.get(f'/learn/group/{work.pk}/'), 'deadline')
        # One word is enough: the other options come from the rest of the language.
        self.assertContains(self.client.get(f'/quiz/?deck={work.pk}'), 'id="quiz-data"')

        other = User.objects.create_user(email='other@example.com', password='x')
        self.client.force_login(other)
        self.assertEqual(self.client.get(f'/learn/group/{work.pk}/').status_code, 404)
        self.assertEqual(self.client.get(f'/quiz/?deck={work.pk}').status_code, 404)

    def test_swipe_answer_via_session(self):
        self.client.force_login(self.user)
        word = Word.objects.filter(language=self.en, owner=None).first()
        self.client.get('/learn/all/')  # sets the csrf cookie
        res = self.client.post(
            '/api/review/answer/', {'word': word.pk, 'direction': 'right'}, content_type='application/json',
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['box_level'], 1)

    def test_language_switch(self):
        self.client.post('/language/', {'language': 'de', 'next': '/grammar/'})
        self.assertContains(self.client.get('/grammar/'), 'DE · справочник')

    def test_add_and_delete_own_word(self):
        self.client.force_login(self.user)
        self.client.get('/words/')  # creates the default «Мои слова» group
        my_words = Deck.objects.get(owner=self.user, is_default=True)
        res = self.client.post('/words/', {
            'text': ' apple ', 'translation': 'яблоко', 'transcription': '', 'part_of_speech': 'noun',
            'level': 'A1', 'example_sentence': '', 'deck': my_words.pk,
        })
        self.assertEqual(res.status_code, 302)
        word = Word.objects.get(owner=self.user)
        self.assertEqual((word.text, word.language), ('apple', self.en))
        self.assertEqual(list(word.decks.all()), [my_words])

        other = User.objects.create_user(email='other@example.com', password='x')
        self.client.force_login(other)
        self.assertEqual(self.client.post(f'/words/{word.pk}/delete/').status_code, 404)
        self.client.force_login(self.user)
        self.client.post(f'/words/{word.pk}/delete/')
        self.assertFalse(Word.objects.filter(pk=word.pk).exists())

    def test_toggle_learned(self):
        rule = GrammarRule.objects.first()
        self.client.force_login(self.user)
        self.client.post(f'/grammar/{rule.pk}/toggle-learned/')
        self.assertTrue(GrammarProgress.objects.filter(user=self.user, rule=rule).exists())
        self.assertContains(self.client.get(f'/grammar/?level={rule.level}'), '1/')
        self.client.post(f'/grammar/{rule.pk}/toggle-learned/')
        self.assertFalse(GrammarProgress.objects.filter(user=self.user, rule=rule).exists())

    def test_only_staff_manage_rules(self):
        rule = GrammarRule.objects.filter(language=self.en, level='A1').first()
        self.client.force_login(self.user)
        self.assertEqual(self.client.get('/grammar/new/').status_code, 403)
        self.assertEqual(self.client.post(f'/grammar/{rule.pk}/delete/').status_code, 403)
        self.assertEqual(self.client.post('/grammar/preview/', {'body': 'x'}).status_code, 403)

        self.client.force_login(self.admin)
        res = self.client.post('/grammar/new/', {'title': ' New ', 'level': 'A1', 'body': '## Hi'})
        new = GrammarRule.objects.get(title='New')
        self.assertRedirects(res, reverse('web:grammar-detail', args=[new.pk]), fetch_redirect_response=False)
        last = GrammarRule.objects.filter(language=self.en, level='A1').exclude(pk=new.pk).order_by('-order').first()
        self.assertEqual(new.order, last.order + 1)

        self.client.post(f'/grammar/{new.pk}/edit/', {'title': 'Renamed', 'level': 'A2', 'body': 'x'})
        new.refresh_from_db()
        self.assertEqual((new.title, new.level), ('Renamed', 'A2'))

        self.assertContains(self.client.post('/grammar/preview/', {'body': '## Hi'}), 'class="rule-h2"')

        self.client.post(f'/grammar/{new.pk}/delete/')
        self.assertFalse(GrammarRule.objects.filter(pk=new.pk).exists())


@override_settings(ADMIN_EMAILS=['owner@example.com'], STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})
class AdministrationTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email='owner@example.com', password='pass12345!x')
        self.admin = User.objects.create_user(email='admin@example.com', password='pass12345!x', is_staff=True)
        self.user = User.objects.create_user(email='user@example.com', password='pass12345!x')

    def act(self, user, action):
        return self.client.post(f'/manage/users/{user.pk}/{action}/')

    def test_only_admins(self):
        self.assertRedirects(self.client.get('/manage/users/'), '/login/?next=/manage/users/', fetch_redirect_response=False)
        self.client.force_login(self.user)
        for url in ['/manage/users/', '/manage/log/']:
            self.assertEqual(self.client.get(url).status_code, 403)
        self.assertEqual(self.act(self.admin, 'revoke_admin').status_code, 403)
        self.assertNotContains(self.client.get('/'), 'Админка')

        self.client.force_login(self.admin)
        self.assertContains(self.client.get('/'), 'Админка')
        self.assertContains(self.client.get('/manage/users/?q=user%40'), 'user@example.com')
        self.assertEqual(self.client.get('/manage/log/').status_code, 200)

    def test_roles_and_blocking_are_logged(self):
        self.client.force_login(self.admin)
        self.act(self.user, 'grant_admin')
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_staff and self.user.is_superuser)
        self.act(self.user, 'revoke_admin')
        self.act(self.user, 'block')
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_staff or self.user.is_active)

        actions = list(ActivityLog.objects.filter(user=self.admin).exclude(action='login').values_list('action', 'target'))
        self.assertEqual(actions, [('user_block', 'user@example.com'), ('admin_revoke', 'user@example.com'),
                                   ('admin_grant', 'user@example.com')])
        self.assertContains(self.client.get('/manage/log/?group=admin'), 'заблокировал пользователя')

        # Neither yourself nor the owners from ADMIN_EMAILS can be changed.
        self.assertEqual(self.act(self.admin, 'revoke_admin').status_code, 403)
        self.assertEqual(self.act(self.owner, 'block').status_code, 403)
        self.assertEqual(self.act(self.user, 'delete_everything').status_code, 403)

    def test_blocked_user_cannot_sign_in(self):
        self.user.is_active = False
        self.user.save()
        res = self.client.post('/login/', {'email': 'user@example.com', 'password': 'pass12345!x'})
        self.assertContains(res, 'Аккаунт заблокирован')
        res = self.client.post('/login/', {'email': 'user@example.com', 'password': 'wrong'})
        self.assertContains(res, 'Неверный email или пароль')
        with patch('apps.users.google.google_id_token.verify_oauth2_token', return_value={'email': 'user@example.com'}), \
                self.settings(GOOGLE_OAUTH_CLIENT_ID='x'):
            res = self.client.post('/auth/google/', {'credential': 't'}, content_type='application/json')
        self.assertEqual(res.status_code, 401)

    def test_user_actions_are_logged(self):
        self.client.post('/login/', {'email': 'user@example.com', 'password': 'wrong'})
        self.client.post('/login/', {'email': 'user@example.com', 'password': 'pass12345!x'},
                         HTTP_X_FORWARDED_FOR='203.0.113.7, 10.0.0.1')
        deck = default_deck(self.user, Language.objects.get(code='en'))
        self.client.post('/words/', {'text': 'goat', 'translation': 'коза', 'level': 'A1', 'part_of_speech': 'noun', 'deck': deck.pk})
        self.client.post('/logout/')
        log = list(ActivityLog.objects.order_by('created_at', 'pk').values_list('action', 'user_email', 'target', 'ip'))
        self.assertEqual(log[0][:2], ('login_failed', 'user@example.com'))
        self.assertEqual(log[1], ('login', 'user@example.com', '', '203.0.113.7'))
        self.assertIn(('word_add', 'user@example.com', 'goat — коза'), [row[:3] for row in log])
        self.assertEqual(log[-1][:2], ('logout', 'user@example.com'))

    def test_password_reset_link(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.post(f'/manage/users/{self.admin.pk}/reset-link/').status_code, 403)

        self.client.force_login(self.admin)
        self.assertEqual(self.client.post(f'/manage/users/{self.admin.pk}/reset-link/').status_code, 403)  # self
        self.assertEqual(self.client.post(f'/manage/users/{self.owner.pk}/reset-link/').status_code, 403)
        res = self.client.post(f'/manage/users/{self.user.pk}/reset-link/')
        link = res.context['link']
        self.assertTrue(link.startswith('http://testserver/reset/'))
        self.assertTrue(ActivityLog.objects.filter(user=self.admin, action='password_link', target=self.user.email).exists())

        self.client.logout()
        path = link.removeprefix('http://testserver')
        self.assertContains(self.client.get(path), 'user@example.com')
        res = self.client.post(path, {'new_password1': 'short', 'new_password2': 'short'})
        self.assertEqual(res.status_code, 200)  # too weak: form errors, password unchanged
        res = self.client.post(path, {'new_password1': 'N3w-pass-word!', 'new_password2': 'N3w-pass-word!'})
        self.assertRedirects(res, '/login/', fetch_redirect_response=False)
        self.assertTrue(self.client.login(email='user@example.com', password='N3w-pass-word!'))
        self.assertTrue(ActivityLog.objects.filter(user=self.user, action='password_reset').exists())

        self.client.logout()
        self.assertContains(self.client.get(path), 'Ссылка недействительна', status_code=400)  # one-time
        self.assertContains(self.client.get('/reset/zzz/bad-token/'), 'Ссылка недействительна', status_code=400)

    def test_database_versions(self):
        import tempfile
        from pathlib import Path

        from .backups import current_fingerprint

        folder = Path(tempfile.mkdtemp())
        same = folder / 'poliglot-2026-10-16_030000-auto.sql.gz'
        other = folder / 'poliglot-2026-10-01_030000-auto.sql.gz'
        for path in (same, other):
            path.write_bytes(b'dump')
        (folder / (same.name + '.meta')).write_text(current_fingerprint())
        (folder / (other.name + '.meta')).write_text('old-schema')
        (folder / 'secret.txt').write_text('not a backup')

        with self.settings(BACKUP_DIR=str(folder)):
            self.client.force_login(self.admin)  # admins aren't owners
            self.assertEqual(self.client.get('/manage/database/').status_code, 403)
            self.assertNotContains(self.client.get('/manage/users/'), 'База данных')

            self.client.force_login(self.owner)
            page = self.client.get('/manage/database/')
            self.assertEqual([b['same_version'] for b in page.context['backups']], [True, False])
            self.assertContains(page, 'другая версия сайта')

            res = self.client.get(f'/manage/database/{same.name}/download/')
            self.assertEqual(b''.join(res.streaming_content), b'dump')
            res.close()
            self.assertEqual(self.client.get('/manage/database/secret.txt/download/').status_code, 404)
            self.assertEqual(self.client.get('/manage/database/..%2Fsecret.txt/download/').status_code, 404)

            self.client.post('/manage/database/backup/')
            self.client.post(f'/manage/database/{same.name}/restore/')  # busy: the backup is still queued
            jobs = sorted(p.read_text() for p in (folder / '.queue').glob('*.job'))
            self.assertEqual(jobs, ['backup'])
            self.assertTrue(self.client.get('/manage/database/').context['busy'])

            for job in (folder / '.queue').glob('*.job'):
                job.unlink()
            self.client.post(f'/manage/database/{same.name}/restore/')
            self.assertEqual([p.read_text() for p in (folder / '.queue').glob('*.job')], [f'restore {same.name}'])
            self.assertEqual(self.client.post('/manage/database/nope.sql.gz/restore/').status_code, 404)

        self.assertEqual(
            list(ActivityLog.objects.filter(user=self.owner).exclude(action='login').values_list('action', flat=True)),
            ['backup_restore', 'backup_create', 'backup_download'],
        )
        with self.settings(BACKUP_DIR=''):
            self.assertContains(self.client.get('/manage/database/'), 'не подключена папка бэкапов')

    def test_database_upload(self):
        import gzip
        import tempfile
        from pathlib import Path

        from django.core.files.uploadedfile import SimpleUploadedFile

        from .backups import fingerprint

        folder = Path(tempfile.mkdtemp())
        dump = (
            '--\r\n-- PostgreSQL database dump\r\n--\r\n'
            'COPY public.django_migrations (id, app, name, applied) FROM stdin;\r\n'
            '2\tusers\t0002_make_admin\t2026-09-16 11:36:16+00\r\n'
            '1\tcore\t0001_initial\t2026-09-16 11:36:16+00\r\n'
            '\\.\r\n'
        ).encode()
        upload = lambda name, content: self.client.post('/manage/database/upload/', {'file': SimpleUploadedFile(name, content)})

        with self.settings(BACKUP_DIR=str(folder)):
            self.client.force_login(self.admin)
            self.assertEqual(upload('a.sql', dump).status_code, 403)  # owners only

            self.client.force_login(self.owner)
            upload('old-server.sql', dump)  # plain, with Windows line endings
            upload('again.sql.gz', gzip.compress(dump))
            saved = sorted(folder.glob('*-uploaded.sql.gz'))
            self.assertEqual(len(saved), 2)
            content = gzip.decompress(saved[0].read_bytes())
            self.assertNotIn(b'\r', content)
            self.assertTrue(content.startswith(b'--\n-- PostgreSQL database dump'))
            expected = fingerprint([('core', '0001_initial'), ('users', '0002_make_admin')])
            self.assertEqual(Path(f'{saved[0]}.meta').read_text(), expected)
            versions = self.client.get('/manage/database/').context['backups']
            self.assertEqual({v['kind'] for v in versions}, {'Загруженный'})
            self.assertEqual({v['same_version'] for v in versions}, {False})  # older schema

            for name, content, error in [
                ('notes.sql', b'hello\n', 'Это не дамп PostgreSQL.'),
                ('broken.sql.gz', b'not gzip', 'Не удалось прочитать файл'),
                ('other.sql', b'--\n-- PostgreSQL database dump\n--\nCREATE TABLE x ();\n', 'бэкап другой базы'),
                ('photo.png', dump, 'Выберите файл .sql или .sql.gz'),
            ]:
                self.assertContains(self.client.post('/manage/database/upload/', {'file': SimpleUploadedFile(name, content)}, follow=True), error)
            self.assertEqual(len(list(folder.glob('*.sql.gz'))), 2)  # nothing left from failed uploads
            self.assertEqual(list(folder.glob('*.part')), [])
        self.assertEqual(ActivityLog.objects.filter(user=self.owner, action='backup_upload').count(), 2)
