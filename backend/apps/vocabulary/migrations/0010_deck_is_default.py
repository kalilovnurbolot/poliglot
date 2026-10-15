from django.db import migrations, models

DEFAULT_DECK_NAME = 'Мои слова'


def move_own_words_to_default_decks(apps, schema_editor):
    """Words users added before groups existed go to their «Мои слова» group."""
    Deck = apps.get_model('vocabulary', 'Deck')
    Word = apps.get_model('vocabulary', 'Word')
    for word in Word.objects.filter(owner__isnull=False, decks__isnull=True):
        deck, _ = Deck.objects.get_or_create(
            owner_id=word.owner_id, language_id=word.language_id, is_default=True,
            defaults={'name': DEFAULT_DECK_NAME},
        )
        word.decks.add(deck)


class Migration(migrations.Migration):

    dependencies = [
        ('vocabulary', '0009_seed_more_vocabulary'),
    ]

    operations = [
        migrations.AddField(
            model_name='deck',
            name='is_default',
            field=models.BooleanField(default=False, help_text="The owner's «Мои слова» group, where new words go unless another is chosen."),
        ),
        migrations.AddConstraint(
            model_name='deck',
            constraint=models.UniqueConstraint(condition=models.Q(('is_default', True)), fields=('owner', 'language'), name='one_default_deck_per_language'),
        ),
        migrations.RunPython(move_own_words_to_default_decks, migrations.RunPython.noop),
    ]
