from django.db import migrations
from django.contrib.auth.models import User

def reset_passwords(apps, schema_editor):
    users = ['admin', 'basil', 'eluomuno']
    for username in users:
        try:
            u = User.objects.get(username=username)
            u.set_password('BasilSecure2026!')
            u.save()
            print(f"Password for user '{username}' reset successfully in migration.")
        except User.DoesNotExist:
            print(f"User '{username}' not found in migration.")

class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0003_loginlog'),
    ]

    operations = [
        migrations.RunPython(reset_passwords),
    ]
