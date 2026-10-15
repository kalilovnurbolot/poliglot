import hashlib
import hmac
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.core.models import Language
from apps.grammar.models import GrammarProgress, GrammarRule
from apps.users.models import User
from apps.vocabulary.models import Word

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

    def test_learn_and_quiz_pages(self):
        self.client.force_login(self.user)
        self.assertContains(self.client.get('/learn/A1/'), 'id="cards-data"')
        self.assertEqual(self.client.get('/learn/Z9/').status_code, 404)
        self.assertContains(self.client.get('/quiz/?level=A1&mode=listening'), 'id="quiz-data"')

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
        res = self.client.post('/words/', {
            'text': ' apple ', 'translation': 'яблоко', 'transcription': '', 'part_of_speech': 'noun',
            'level': 'A1', 'example_sentence': '',
        })
        self.assertEqual(res.status_code, 302)
        word = Word.objects.get(owner=self.user)
        self.assertEqual((word.text, word.language), ('apple', self.en))

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
