import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_task_management.settings')

app = Celery('smart_task_management')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    'send-deadline-reminders-every-hour': {
        'task': 'tasks.tasks.send_deadline_reminders',
        'schedule': crontab(minute=0),  # Every hour
    },
    'send-daily-task-summary': {
        'task': 'tasks.tasks.send_daily_task_summary',
        'schedule': crontab(hour=8, minute=0),  # Every day at 8 AM
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

