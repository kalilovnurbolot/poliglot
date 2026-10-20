from django.conf import settings
from django.db import models

from apps.core.models import Language, Level


class Mission(models.Model):
    """A role-play scene: the player talks to a character step by step to reach a goal."""

    class Scene(models.TextChoices):
        SHOP = 'shop', 'Магазин'
        CAFE = 'cafe', 'Кафе'
        BAKERY = 'bakery', 'Пекарня'
        AIRPORT = 'airport', 'Аэропорт'
        HOTEL = 'hotel', 'Отель'
        POLICE = 'police', 'Полиция'
        MUSEUM = 'museum', 'Музей'

    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='missions')
    level = models.CharField(max_length=2, choices=Level.choices, default=Level.A1)
    title = models.CharField(max_length=200)
    briefing = models.TextField(help_text='Задание для игрока, по-русски.')
    teaser = models.CharField(max_length=300, blank=True, help_text='Завязка сюжета для карты миссий, по-русски.')
    scene = models.CharField(max_length=20, choices=Scene.choices, default=Scene.SHOP)
    npc_name = models.CharField(max_length=50, default='Продавец')
    target_words = models.JSONField(default=list, blank=True, help_text='Слова, которые нужно использовать: ["bread", "how much"].')
    retry_line = models.CharField(max_length=200, help_text='Что говорит персонаж, если не понял игрока.')
    farewell_line = models.CharField(max_length=200, help_text='Последняя реплика персонажа.')
    order = models.PositiveIntegerField(default=0)
    map_x = models.PositiveSmallIntegerField(null=True, blank=True, help_text='Точка на карте миссий, 0–100 % слева направо.')
    map_y = models.PositiveSmallIntegerField(null=True, blank=True, help_text='Точка на карте миссий, 0–100 % сверху вниз.')
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['level', 'order']

    def __str__(self):
        return f'[{self.level}] {self.title}'


class MissionStep(models.Model):
    """One exchange: the character says `npc_line`, the player must answer reaching `goal`."""
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='steps')
    order = models.PositiveIntegerField(default=0)
    npc_line = models.CharField(max_length=300)
    npc_line_ru = models.CharField(max_length=300, blank=True, help_text='Перевод реплики для субтитров.')
    goal = models.CharField(max_length=200, help_text='Что нужно сделать, по-русски: «Попросите хлеб».')
    keywords = models.JSONField(
        default=list,
        help_text='Группы слов, каждая должна прозвучать хотя бы одним вариантом: [["bread", "loaf"], ["please"]].',
    )
    patterns = models.JSONField(default=list, help_text='Образцовые ответы, первый показывается как подсказка.')

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.mission.title} #{self.order}: {self.goal}'


class MissionAttempt(models.Model):
    """A finished playthrough with its scores (see scoring.summarize)."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mission_attempts')
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='attempts')
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField(auto_now_add=True)
    total = models.PositiveSmallIntegerField()
    stars = models.PositiveSmallIntegerField()
    scores = models.JSONField(help_text='{"task": 0..100, "words": ..., "grammar": ..., "pronunciation": ... | null, "fluency": ...}')
    feedback = models.JSONField(default=list)
    transcript = models.JSONField(default=list)

    class Meta:
        ordering = ['-finished_at']

    def __str__(self):
        return f'{self.user} — {self.mission} ({self.total})'
