import os
import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home.settings')
django.setup()

# Run migrations automatically at startup
try:
    call_command('makemigrations', interactive=False)
    call_command('migrate', interactive=False)
    call_command('collectstatic', interactive=False, verbosity=0)
except Exception as e:
    print(f"Migration error: {e}")
