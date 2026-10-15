from django.conf import settings
from django.db import migrations


def make_admins(apps, schema_editor):
    User = apps.get_model('users', 'User')
    for email in settings.ADMIN_EMAILS:
        User.objects.filter(email__iexact=email).update(is_staff=True, is_superuser=True)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(make_admins, migrations.RunPython.noop),
    ]
