from django.db import migrations


def seed_german(apps, schema_editor):
    Language = apps.get_model('core', 'Language')
    Language.objects.get_or_create(code='de', defaults={'name': 'Немецкий'})
    # Keep language names consistent (Russian UI) now that there's more than one.
    Language.objects.filter(code='en').update(name='Английский')


def remove_german(apps, schema_editor):
    Language = apps.get_model('core', 'Language')
    Language.objects.filter(code='de').delete()
    Language.objects.filter(code='en').update(name='English')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_seed_english_language'),
    ]

    operations = [
        migrations.RunPython(seed_german, remove_german),
    ]
