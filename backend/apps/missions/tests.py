import io
import json
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.utils import timezone

from apps.users.models import ActivityLog, User
from apps.vocabulary.models import UserWordProgress, Word

from . import meaning
from .pronunciation import score_pronunciation
from .grammar_check import check_grammar, sentence_case
from .models import Mission, MissionAttempt
from .scoring import evaluate_step, normalize, summarize


def words(text, conf=1.0, gap=0.05):
    """Word details as the voice service returns them, evenly spaced."""
    result, t = [], 0.0
    for w in text.split():
        result.append({'word': w, 'conf': conf, 'start': t, 'end': t + 0.3})
        t += 0.3 + gap
    return result


class ScoringTests(TestCase):
    def setUp(self):
        # The seeded English shop mission (migrations/0002_seed_missions.py).
        self.mission = Mission.objects.get(title='В магазине')
        self.steps = list(self.mission.steps.all())

    def test_normalize_expands_contractions(self):
        self.assertEqual(normalize("I'd like it, please!", 'en'), ['i', 'would', 'like', 'it', 'please'])
        self.assertEqual(normalize('Ich möchte Brötchen.', 'de'), ['ich', 'möchte', 'brötchen'])

    def test_step_needs_every_keyword_group(self):
        step = self.steps[0]
        good = evaluate_step(step, 'Hello, can I have some bread, please?', [], 'en')
        self.assertTrue(good['passed'])
        self.assertEqual(good['similarity'], 1.0)
        self.assertIsNone(good['confidence'])

        self.assertFalse(evaluate_step(step, 'Hello, can I have some milk?', [], 'en')['passed'])
        self.assertEqual(evaluate_step(step, 'milk', [], 'en')['missing'], ['bread'])
        self.assertTrue(evaluate_step(step, 'a loaf', [], 'en')['passed'])
        self.assertFalse(evaluate_step(step, 'breadcrumbs', [], 'en')['passed'])  # whole words only
        self.assertTrue(evaluate_step(self.steps[2], 'how much is it', [], 'en')['passed'])  # multi-word keyword

    def test_word_details_give_pronunciation_and_fluency(self):
        step = self.steps[0]
        result = evaluate_step(step, 'can i have bread', words('can i have bread', gap=1.0), 'en')
        self.assertEqual(result['pauses'], 3)
        self.assertEqual(result['confidence'], 1.0)

        heard = words('can i have bread')
        heard[3]['conf'] = 0.4
        self.assertEqual(evaluate_step(step, 'can i have bread', heard, 'en')['unclear'], ['bread'])

    def test_perfect_playthrough(self):
        answers = [evaluate_step(s, s.patterns[0], words(s.patterns[0].lower()), 'en') for s in self.steps]
        summary = summarize(self.mission, self.steps, answers)
        self.assertEqual(summary['scores'], {'task': 100, 'words': 100, 'grammar': 100, 'pronunciation': 100, 'fluency': 100})
        self.assertEqual((summary['total'], summary['stars']), (100, 3))
        self.assertEqual(summary['feedback'], ['Отлично! Вы справились без единой ошибки.'])

    def test_short_answers_retries_and_skips_cost_points(self):
        steps = self.steps
        answers = [
            evaluate_step(steps[0], 'milk', [], 'en'),  # misunderstood
            evaluate_step(steps[0], 'bread', [], 'en'),  # one word instead of a sentence
            evaluate_step(steps[1], 'milk', [], 'en'),
            evaluate_step(steps[2], 'how much', [], 'en'),
        ]
        summary = summarize(self.mission, steps, answers, skipped=[4, 5])
        scores = summary['scores']
        self.assertEqual(scores['task'], 60)
        self.assertIsNone(scores['pronunciation'])  # typed answers: not scored, not weighed
        self.assertEqual(scores['fluency'], 90)
        self.assertLess(scores['grammar'], 60)
        self.assertLess(scores['words'], 100)
        self.assertLess(summary['stars'], 3)
        feedback = ' '.join(summary['feedback'])
        self.assertIn('Пропущен шаг: Скажите, что заплатите картой.', feedback)
        self.assertIn('please', feedback)
        self.assertIn('«bread» — можно сказать полнее', feedback)
        self.assertIn('переспрашивал 1 раз', feedback)

    def test_unclear_pronunciation_lowers_the_score(self):
        answers = [evaluate_step(s, s.patterns[0], words(s.patterns[0].lower(), conf=0.6), 'en') for s in self.steps]
        summary = summarize(self.mission, self.steps, answers)
        self.assertEqual(summary['scores']['pronunciation'], 20)
        self.assertTrue(any(line.startswith('Произнесите чётче') for line in summary['feedback']))

    def test_grammar_mistakes_cost_points(self):
        grammar = {'errors': [{'wrong': 'buy', 'fix': 'to buy', 'message': 'Did you mean “to buy”?'}],
                   'corrected': 'I want to buy bread please'}
        first = evaluate_step(self.steps[0], 'I want buy bread please', [], 'en', grammar)
        self.assertTrue(first['passed'])
        self.assertEqual(first['corrected'], 'I want to buy bread please')
        rest = [evaluate_step(s, s.patterns[0], [], 'en', {'errors': [], 'corrected': s.patterns[0]}) for s in self.steps[1:]]
        self.assertIsNone(rest[0]['corrected'])

        clean = summarize(self.mission, self.steps, [evaluate_step(self.steps[0], 'I want buy bread please', [], 'en'), *rest])
        summary = summarize(self.mission, self.steps, [first, *rest])
        self.assertAlmostEqual(clean['scores']['grammar'] - summary['scores']['grammar'], 15, delta=1)  # rounding
        self.assertIn('Ошибка: «I want buy bread please» → «I want to buy bread please».', summary['feedback'])
        self.assertFalse(any('можно сказать полнее' in line and 'want buy' in line for line in summary['feedback']))

    def test_meaning_accepts_paraphrases_of_its_own_step_only(self):
        price = self.steps[2]
        self.assertFalse(evaluate_step(price, 'what is the total', [], 'en')['passed'])  # no keywords
        paraphrase = evaluate_step(price, 'what is the total', [], 'en', meaning={'own': 0.83, 'other': 0.62})
        self.assertTrue(paraphrase['passed'])
        self.assertEqual(paraphrase['meaning'], 0.83)
        # Close to its step, but as close to another one ("that is all" of the price step).
        self.assertFalse(evaluate_step(price, 'yes that is everything', [], 'en', meaning={'own': 0.78, 'other': 0.65})['passed'])
        self.assertFalse(evaluate_step(self.steps[0], 'can i have some milk', [], 'en', meaning={'own': 0.39, 'other': 0.94})['passed'])
        self.assertTrue(evaluate_step(self.steps[4], 'cheers see you', [], 'en', meaning={'own': 0.95, 'other': 0.89})['passed'])
        self.assertFalse(evaluate_step(self.steps[4], 'cheers see you', [], 'en', meaning={'own': 0.92, 'other': 0.93})['passed'])

        answers = [evaluate_step(s, s.patterns[0], [], 'en') for s in self.steps]
        answers[2] = paraphrase
        summary = summarize(self.mission, self.steps, answers)
        self.assertEqual(summary['scores']['grammar'], 100)  # a whole phrase meaning the same is well built
        self.assertFalse(any('what is the total' in line for line in summary['feedback']))

    def test_sounds_replace_confidence_and_give_advice(self):
        def sound(word, expected, heard, score, subs=()):
            return {'word': word, 'expected': expected, 'heard': heard, 'score': score, 'subs': [list(s) for s in subs]}
        answers = [evaluate_step(s, s.patterns[0], words(s.patterns[0].lower()), 'en') for s in self.steps]
        answers[0] = evaluate_step(self.steps[0], 'can i have bread', words('can i have bread', conf=0.6), 'en', sounds=[
            sound('can', 'kæn', 'kɛn', 0.67, [('æ', 'ɛ')]), sound('i', 'aɪ', 'aɪ', 1.0),
            sound('have', 'hæv', 'hæv', 1.0), sound('bread', 'brɛd', 'brɛt', 0.75, [('d', 't')]),
        ])
        self.assertEqual(answers[0]['mispronounced'], ['can', 'bread'])
        summary = summarize(self.mission, self.steps, answers)
        self.assertEqual(summary['scores']['pronunciation'], 86)  # sounds, not the 0.6 confidence
        feedback = summary['feedback']
        self.assertIn('Произношение «can»: нужно [kæn], прозвучало [kɛn].', feedback)
        self.assertIn('Произношение «bread»: нужно [brɛd], прозвучало [brɛt].', feedback)
        self.assertTrue(any(line.startswith('æ в «can»') for line in feedback))
        self.assertTrue(any(line.startswith('звонкое d') for line in feedback))
        self.assertFalse(any(line.startswith('Произнесите чётче') for line in feedback))
        self.assertEqual(summary['unclear'][:2], ['can', 'bread'])


def lt_response(matches):
    return io.BytesIO(json.dumps({'matches': matches}).encode())


def lt_match(offset, length, category, fix):
    return {'offset': offset, 'length': length, 'message': 'msg', 'rule': {'category': {'id': category}},
            'replacements': [{'value': fix}] if fix else []}


class GrammarCheckTests(TestCase):
    def test_sentence_case(self):
        self.assertEqual(sentence_case("can i have it, i'm sure", 'en'), "Can I have it, I'm sure")
        self.assertEqual(sentence_case('ich möchte ein brot', 'de'), 'Ich möchte ein brot')

    def test_off_without_service(self):
        self.assertIsNone(check_grammar('I want buy bread', 'en'))

    @override_settings(GRAMMAR_SERVICE_URL='http://grammar:8010')
    @patch('apps.missions.grammar_check.urlopen')
    def test_only_grammar_mistakes_are_fixed(self, urlopen):
        urlopen.return_value = lt_response([
            lt_match(0, 1, 'TYPOS', 'I'),  # lowercase "i" from speech recognition: ignored
            lt_match(7, 3, 'GRAMMAR', 'to buy'),
            lt_match(11, 5, 'GRAMMAR', 'breads'),
        ])
        result = check_grammar('i want buy bread', 'en')
        self.assertEqual(result['corrected'], 'I want to buy breads')
        self.assertIn(b'text=I+want+buy+bread', urlopen.call_args.args[1])
        self.assertEqual([e['wrong'] for e in result['errors']], ['buy', 'bread'])
        url, body = urlopen.call_args.args
        self.assertEqual(url, 'http://grammar:8010/v2/check')
        self.assertIn(b'language=en-US', body)

        self.assertIsNone(check_grammar('hallo', 'ru'))
        urlopen.side_effect = OSError
        self.assertIsNone(check_grammar('I want buy bread', 'en'))


class MeaningTests(TestCase):
    def setUp(self):
        meaning._cache.clear()
        self.steps = list(Mission.objects.get(title='В магазине').steps.all())

    def test_off_without_service(self):
        self.assertIsNone(meaning.meaning_match('what is the total', self.steps[2], self.steps))

    @override_settings(MEANING_SERVICE_URL='http://meaning:8020')
    @patch('apps.missions.meaning.urlopen')
    def test_closeness_to_own_and_other_steps(self, urlopen):
        price = self.steps[2]
        def respond(request, timeout):
            texts = json.loads(request.data)['texts']
            # "price" phrases point one way, everything else another.
            vectors = [[0.8, 0.6] if t == 'what is the total' else [1, 0] if t in price.patterns else [0, 1] for t in texts]
            return io.BytesIO(json.dumps({'vectors': vectors}).encode())
        urlopen.side_effect = respond

        self.assertEqual(meaning.meaning_match('what is the total', price, self.steps), {'own': 0.8, 'other': 0.6})
        self.assertEqual(urlopen.call_args.args[0].full_url, 'http://meaning:8020/embed')
        # Sample answers are cached: the next answer asks for its own vector only.
        meaning.meaning_match('how much', price, self.steps)
        self.assertEqual(json.loads(urlopen.call_args.args[0].data), {'texts': ['how much']})

        urlopen.side_effect = OSError
        self.assertIsNone(meaning.meaning_match('something new', price, self.steps))


class PronunciationTests(TestCase):
    def test_off_without_service(self):
        self.assertIsNone(score_pronunciation(b'\0\0', 'hello', 'en'))

    @override_settings(PRONOUNCE_SERVICE_URL='http://pronounce:8030')
    @patch('apps.missions.pronunciation.urlopen')
    def test_scores_recording(self, urlopen):
        urlopen.return_value = io.BytesIO(b'{"score": 0.9, "words": []}')
        self.assertEqual(score_pronunciation(b'\0\0', 'i think', 'en'), {'score': 0.9, 'words': []})
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, 'http://pronounce:8030/score?language=en&text=i+think')
        self.assertEqual(request.data, b'\0\0')
        self.assertIsNone(score_pronunciation(b'\0\0', '', 'en'))  # nothing recognized
        urlopen.side_effect = OSError
        self.assertIsNone(score_pronunciation(b'\0\0', 'i think', 'en'))


@override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})
class MissionPagesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='player@example.com', password='pass12345')
        self.mission = Mission.objects.get(title='В магазине')
        self.url = f'/missions/{self.mission.pk}/'
        self.step_url = f'{self.url}step/'

    def post(self, data):
        return self.client.post(self.step_url, json.dumps(data), content_type='application/json')

    def test_list_and_login(self):
        self.assertEqual(self.client.get('/missions/').status_code, 302)
        self.client.force_login(self.user)
        page = self.client.get('/missions/')
        self.assertContains(page, 'В магазине')
        self.assertNotContains(page, 'В пекарне')  # German, other language
        self.assertContains(self.client.get(self.url), 'id="mission-config"')

    def test_map_opens_chapters_in_order(self):
        self.client.force_login(self.user)
        cafe = Mission.objects.get(title='В кафе')
        page = self.client.get('/missions/')
        self.assertContains(page, 'Пропавший чемодан')  # the story, after the first two
        self.assertContains(page, 'Откроется после главы «В магазине»')
        self.assertContains(page, 'map-pin is-current', count=1)
        self.assertRedirects(self.client.get(f'/missions/{cafe.pk}/'), '/missions/')

        attempt = MissionAttempt.objects.create(
            user=self.user, mission=self.mission, started_at=timezone.now(),
            total=50, stars=1, scores={},
        )
        self.assertContains(self.client.get(f'/missions/{cafe.pk}/'), 'id="mission-config"')
        result = self.client.get(f'/missions/attempt/{attempt.pk}/')
        self.assertContains(result, 'Глава 2 открыта')
        self.assertContains(result, cafe.teaser)

    def test_playthrough(self):
        Word.objects.get_or_create(language=self.mission.language, owner=None, text='bread', defaults={'translation': 'хлеб'})
        self.client.force_login(self.user)
        self.assertEqual(self.post({'text': 'hello'}).status_code, 400)  # not started
        self.client.get(self.url)

        reply = self.post({'text': 'I want milk'}).json()
        self.assertFalse(reply['passed'])
        self.assertNotIn('hint', reply)
        self.assertEqual(self.post({'skip': True}).status_code, 400)  # too early to skip
        reply = self.post({'text': 'milk again'}).json()
        self.assertTrue(reply['canSkip'])
        self.assertEqual(reply['hint'], 'Hello, can I have some bread, please?')

        reply = self.post({'text': 'Can I have some bread, please?', 'words': words('can i have some bread please')}).json()
        self.assertTrue(reply['passed'])
        self.assertEqual(reply['next']['goal'], 'Попросите молоко')
        self.assertEqual(reply['usedWords'], ['bread', 'milk', 'please'])

        for text in ['Some milk, please.', 'How much is it?', 'Can I pay by card?']:
            self.assertTrue(self.post({'text': text}).json()['passed'])
        reply = self.post({'text': 'Thank you, goodbye!'}).json()
        self.assertTrue(reply['done'])

        attempt = MissionAttempt.objects.get(user=self.user)
        self.assertEqual(reply['resultUrl'], f'/missions/attempt/{attempt.pk}/')
        self.assertEqual(attempt.scores['task'], 100)
        self.assertEqual(len(attempt.transcript), 7)
        progress = UserWordProgress.objects.filter(user=self.user, word__text__iexact='bread')
        self.assertTrue(progress and all(p.correct_count == 1 for p in progress))
        self.assertTrue(ActivityLog.objects.filter(action=ActivityLog.Action.MISSION_COMPLETE).exists())
        self.assertEqual(self.post({'text': 'again'}).status_code, 400)  # finished

        page = self.client.get(reply['resultUrl'])
        self.assertContains(page, 'Выполнение задания')
        self.assertContains(self.client.get('/missions/'), 'Лучший результат')

        self.client.get(self.url)
        fixed = {'errors': [{'wrong': 'has', 'fix': 'have', 'message': 'msg'}], 'corrected': 'Can I have bread'}
        with (patch('apps.web.mission_views.check_grammar', return_value=fixed) as check,
              patch('apps.web.mission_views.meaning_match', return_value={'own': 0.9, 'other': 0.3}) as match):
            self.post({'text': 'Can I has bread'})
            self.assertTrue(self.post({'text': 'a cold drink from the fridge'}).json()['passed'])  # no keyword, same meaning
        check.assert_any_call('Can I has bread', 'en')
        sounds = {'score': 0.5, 'words': [{'word': 'tea', 'expected': 'tiː', 'heard': 'ti', 'score': 0.5, 'subs': [['iː', 'i']]}]}
        self.post({'text': 'tea', 'pronunciation': sounds})
        self.post({'text': 'tea', 'pronunciation': {'words': [{'word': 'x'}]}})  # malformed: ignored
        answers = self.client.session[f'mission:{self.mission.pk}']['answers']
        self.assertEqual(answers[-2]['mispronounced'], ['tea'])
        self.assertIsNone(answers[-1]['sounds'])
        self.assertEqual(match.call_args.args[1].goal, 'Попросите молоко')
        self.assertEqual(self.client.session[f'mission:{self.mission.pk}']['answers'][0]['corrected'], 'Can I have bread')

        other = User.objects.create_user(email='other@example.com', password='pass12345')
        self.client.force_login(other)
        self.assertEqual(self.client.get(reply['resultUrl']).status_code, 404)
