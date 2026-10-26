from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import Language, Level


class Deck(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='decks')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='decks',
        null=True,
        blank=True,
        help_text='Empty for system decks available to everyone.',
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(
        default=False, help_text="The owner's «Мои слова» group, where new words go unless another is chosen.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'language'], condition=models.Q(is_default=True), name='one_default_deck_per_language',
            ),
        ]

    def __str__(self):
        return self.name


class PartOfSpeech(models.TextChoices):
    NOUN = 'noun', 'Noun'
    VERB = 'verb', 'Verb'
    ADJECTIVE = 'adjective', 'Adjective'
    ADVERB = 'adverb', 'Adverb'
    PHRASE = 'phrase', 'Phrase'
    OTHER = 'other', 'Other'


class Word(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='words')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='words',
        null=True,
        blank=True,
        help_text='Empty for system words available to everyone.',
    )
    decks = models.ManyToManyField(Deck, related_name='words', blank=True)
    text = models.CharField(max_length=200)
    translation = models.CharField(max_length=200)
    transcription = models.CharField(max_length=100, blank=True)
    example_sentence = models.TextField(blank=True)
    part_of_speech = models.CharField(
        max_length=20, choices=PartOfSpeech.choices, default=PartOfSpeech.OTHER
    )
    level = models.CharField(max_length=2, choices=Level.choices, default=Level.A1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['text']

    def __str__(self):
        return f'{self.text} — {self.translation}'


class UserWordProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='word_progress')
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='progress_entries')
    box_level = models.PositiveSmallIntegerField(default=0)
    next_review_at = models.DateTimeField(default=timezone.now)
    correct_count = models.PositiveIntegerField(default=0)
    wrong_count = models.PositiveIntegerField(default=0)
    last_result = models.CharField(
        max_length=10,
        choices=[('correct', 'Correct'), ('wrong', 'Wrong')],
        null=True,
        blank=True,
    )
    is_favorite = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'word')
        ordering = ['next_review_at']

    def __str__(self):
        return f'{self.user} — {self.word} (box {self.box_level})'


class IrregularVerb(models.Model):
    """A row of the irregular verbs table: the three forms with their transcriptions.

    A form may have variants separated by " / " ("was / were", "learnt / learned"); any of them counts.
    """

    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='irregular_verbs')
    infinitive = models.CharField(max_length=50)
    infinitive_transcription = models.CharField(max_length=60, blank=True)
    past = models.CharField(max_length=50)
    past_transcription = models.CharField(max_length=60, blank=True)
    participle = models.CharField(max_length=50)
    participle_transcription = models.CharField(max_length=60, blank=True)
    translation = models.CharField(max_length=100)

    class Meta:
        ordering = ['infinitive']
        constraints = [
            models.UniqueConstraint(fields=['language', 'infinitive'], name='unique_irregular_verb'),
        ]

    def __str__(self):
        return f'{self.infinitive} — {self.past} — {self.participle}'

    @property
    def forms(self):
        return [
            (self.infinitive, self.infinitive_transcription),
            (self.past, self.past_transcription),
            (self.participle, self.participle_transcription),
        ]
