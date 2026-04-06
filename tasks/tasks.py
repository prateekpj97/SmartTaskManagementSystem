from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from .models import Task
from django.conf import settings


@shared_task
def send_deadline_reminders():
    """
    Send email reminders for tasks with upcoming deadlines (within 24 hours)
    Optimized with bulk operations and better error handling
    """
    now = timezone.now()
    tomorrow = now + timedelta(hours=24)

    # Optimized: Prefetch user profile in single query
    upcoming_tasks = Task.objects.filter(
        deadline__gte=now,
        deadline__lte=tomorrow,
        status__in=['pending', 'in_progress'],
        reminder_sent=False
    ).select_related('user__profile', 'category').only(
        'id', 'title', 'priority', 'deadline', 'description', 'reminder_sent',
        'user__id', 'user__email', 'user__first_name', 'user__last_name', 'user__username',
        'user__profile__email_notifications',
        'category__name'
    )

    tasks_to_update = []
    sent_count = 0
    failed_emails = []

    for task in upcoming_tasks:
        if not (task.user.profile.email_notifications and task.user.email):
            continue

        subject = f'Reminder: Task "{task.title}" deadline approaching'
        message = f"""
Hello {task.user.get_full_name() or task.user.username},
This is a reminder that your task is due soon:

Task: {task.title}
Priority: {task.get_priority_display()}
Deadline: {task.deadline.strftime('%Y-%m-%d %H:%M')}
Category: {task.category.name if task.category else 'No category'}

Description:
{task.description or 'No description provided'}

Please complete this task before the deadline.

Best regards,
Smart Task Management System
        """

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [task.user.email],
                fail_silently=False,
            )
            task.reminder_sent = True
            tasks_to_update.append(task)
            sent_count += 1
        except Exception as e:
            failed_emails.append(f"{task.user.email}: {str(e)}")

    # Optimized: Bulk update instead of individual saves
    if tasks_to_update:
        Task.objects.bulk_update(tasks_to_update, ['reminder_sent'])

    result = f"Sent {sent_count} deadline reminders"
    if failed_emails:
        result += f". Failed: {len(failed_emails)}"

    return result


@shared_task
def send_daily_task_summary():
    """
    Send daily task summary to all users with email notifications enabled
    Optimized with aggregation and bulk queries
    """
    from django.db.models import Count, Q

    # Optimized: Get users with aggregated stats in one query
    now = timezone.now()
    today = now.date()

    users = User.objects.filter(
        profile__email_notifications=True,
        email__isnull=False
    ).exclude(email='').select_related('profile')

    sent_count = 0
    failed_count = 0

    for user in users:
        # Optimized: Use aggregate to get all counts in single query
        stats = Task.objects.filter(user=user).aggregate(
            pending=Count('id', filter=Q(status='pending')),
            in_progress=Count('id', filter=Q(status='in_progress')),
            completed_today=Count('id', filter=Q(
                status='completed',
                completed_at__date=today
            )),
            overdue=Count('id', filter=Q(
                deadline__lt=now,
                status__in=['pending', 'in_progress']
            ))
        )

        # Skip if no active tasks
        if stats['pending'] + stats['in_progress'] + stats['overdue'] == 0:
            continue

        subject = 'Daily Task Summary'
        message = f"""
Hello {user.get_full_name() or user.username},

Here's your daily task summary:

Pending Tasks: {stats['pending']}
In Progress: {stats['in_progress']}
Completed Today: {stats['completed_today']}
Overdue Tasks: {stats['overdue']}

"""

        if stats['overdue'] > 0:
            message += "\nOverdue Tasks:\n"
            # Optimized: Only fetch required fields
            overdue_tasks = Task.objects.filter(
                user=user,
                deadline__lt=now,
                status__in=['pending', 'in_progress']
            ).only('title', 'deadline').order_by('deadline')[:5]

            for task in overdue_tasks:
                message += f"- {task.title} (Due: {task.deadline.strftime('%Y-%m-%d')})\n"

        message += """
Keep up the good work!

Best regards,
Smart Task Management System
        """

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            sent_count += 1
        except Exception as e:
            failed_count += 1

    return f"Sent {sent_count} daily summaries. Failed: {failed_count}"


@shared_task
def send_task_notification(task_id, notification_type):
    """
    Send notification for specific task events
    """
    try:
        task = Task.objects.select_related('user', 'category').get(id=task_id)
        
        if not task.user.profile.email_notifications or not task.user.email:
            return "Email notifications disabled or no email"
        
        subject_map = {
            'created': f'New Task Created: {task.title}',
            'updated': f'Task Updated: {task.title}',
            'completed': f'Task Completed: {task.title}',
        }
        
        subject = subject_map.get(notification_type, f'Task Notification: {task.title}')
        message = f"""
Hello {task.user.get_full_name() or task.user.username},

Your task has been {notification_type}:

Task: {task.title}
Status: {task.get_status_display()}
Priority: {task.get_priority_display()}
{f'Deadline: {task.deadline.strftime("%Y-%m-%d %H:%M")}' if task.deadline else ''}

Best regards,
Smart Task Management System
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [task.user.email],
            fail_silently=False,
        )
        
        return f"Notification sent for task {task_id}"
    except Task.DoesNotExist:
        return f"Task {task_id} not found"
    except Exception as e:
        return f"Failed to send notification: {str(e)}"

