"""Run: python -m unittest test_phones (no model or espeak needed)."""

import unittest

from phones import align, phones


class AlignTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(phones('ˈb ɹ ɛ d'), ['b', 'r', 'ɛ', 'd'])
        self.assertEqual(phones('ɕ iɛ5'), ['ʃ', 'iɛ'])

    def test_native_pronunciation(self):
        words = [('i', phones('aɪ')), ('think', phones('θ ɪ ŋ k'))]
        result = align(words, phones('aɪ θ ɪ ŋ k'))
        self.assertEqual([w['score'] for w in result], [1.0, 1.0])
        self.assertEqual(result[1]['heard'], 'θɪŋk')

    def test_replaced_sound(self):
        words = [('i', phones('aɪ')), ('think', phones('θ ɪ ŋ k')), ('so', phones('s oʊ'))]
        result = align(words, phones('aɪ s ɪ ŋ k s oʊ'))
        self.assertEqual(result[1]['score'], 0.75)
        self.assertEqual(result[1]['subs'], [['θ', 's']])
        self.assertEqual(result[1]['heard'], 'sɪŋk')
        self.assertEqual(result[2]['score'], 1.0)

    def test_dropped_and_close_sounds(self):
        words = [('can', phones('k æ n')), ('please', phones('p l iː z'))]
        result = align(words, phones('æ n p l iː s'))
        self.assertEqual(result[0]['subs'], [['k', '']])
        self.assertEqual(result[1]['subs'], [['z', 's']])
        # ç/ʃ is a half mistake: the model mixes them up even for native speakers.
        self.assertEqual(align([('ich', phones('ɪ ç'))], phones('ɪ ʃ'))[0]['score'], 0.75)


if __name__ == '__main__':
    unittest.main()
