from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.core.models import Language

from .models import GrammarRule

User = get_user_model()


class GrammarRuleApiTests(APITestCase):
    def setUp(self):
        self.language = Language.objects.get(code='en')
        self.admin = User.objects.create_user(email='admin@example.com', password='pass12345', is_staff=True)
        self.user = User.objects.create_user(email='user@example.com', password='pass12345')
        self.data = {'language': self.language.id, 'title': 'New rule', 'level': 'A1', 'body': '## Hi'}

    def test_anonymous_cannot_create(self):
        res = self.client.post('/api/grammar-rules/', self.data, format='json')
        self.assertEqual(res.status_code, 401)

    def test_regular_user_cannot_create_edit_or_delete(self):
        rule = GrammarRule.objects.first()
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.post('/api/grammar-rules/', self.data, format='json').status_code, 403)
        res = self.client.patch(f'/api/grammar-rules/{rule.id}/', {'title': 'Hacked'}, format='json')
        self.assertEqual(res.status_code, 403)
        self.assertEqual(self.client.delete(f'/api/grammar-rules/{rule.id}/').status_code, 403)

    def test_admin_rule_is_visible_to_everyone_and_goes_last(self):
        self.client.force_authenticate(self.admin)
        res = self.client.post('/api/grammar-rules/', self.data, format='json')
        self.assertEqual(res.status_code, 201)
        rule = GrammarRule.objects.get(id=res.data['id'])
        others = GrammarRule.objects.filter(language=self.language, level='A1').exclude(id=rule.id)
        self.assertGreater(rule.order, max(r.order for r in others))

        self.client.force_authenticate(None)
        ids = [r['id'] for r in self.client.get('/api/grammar-rules/?language=en').data]
        self.assertIn(rule.id, ids)

    def test_admin_can_edit_and_delete(self):
        rule = GrammarRule.objects.first()
        self.client.force_authenticate(self.admin)
        res = self.client.patch(f'/api/grammar-rules/{rule.id}/', {'title': 'Renamed'}, format='json')
        self.assertEqual(res.data['title'], 'Renamed')
        self.assertEqual(self.client.delete(f'/api/grammar-rules/{rule.id}/').status_code, 204)

    def test_user_can_still_mark_rule_learned(self):
        rule = GrammarRule.objects.first()
        self.client.force_authenticate(self.user)
        res = self.client.post(f'/api/grammar-rules/{rule.id}/toggle-learned/')
        self.assertEqual(res.data, {'is_learned': True})
