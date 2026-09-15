from django.db import models


class Level(models.TextChoices):
    """CEFR proficiency levels, shared by grammar rules and vocabulary."""
    A1 = 'A1', 'A1'
    A2 = 'A2', 'A2'
    B1 = 'B1', 'B1'
    B2 = 'B2', 'B2'
    C1 = 'C1', 'C1'
    C2 = 'C2', 'C2'


class Language(models.Model):
    code = models.CharField(max_length=10, unique=True, help_text="ISO 639-1, e.g. 'en'")
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
