from django.conf import settings
from django.db import models

from apps.core.models import Language, Level


class GrammarRule(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='grammar_rules')
    title = models.CharField(max_length=200)
    level = models.CharField(max_length=2, choices=Level.choices, default=Level.A1)
    body = models.TextField(help_text='Markdown-форматированное объяснение с примерами.')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['level', 'order']

    def __str__(self):
        return f'[{self.level}] {self.title}'


class GrammarProgress(models.Model):
    """A row means the user has marked this rule as learned."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='grammar_progress')
    rule = models.ForeignKey(GrammarRule, on_delete=models.CASCADE, related_name='progress_entries')
    learned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'rule')

    def __str__(self):
        return f'{self.user} learned {self.rule}'
