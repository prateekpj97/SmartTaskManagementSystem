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
    """
    now = timezone.now()
    tomorrow = now + timedelta(hours=24)
    
    # Get tasks with deadlines in the next 24 hours that haven't been reminded
    upcoming_tasks = Task.objects.filter(
        deadline__gte=now,
        deadline__lte=tomorrow,
        status__in=['pending', 'in_progress'],
        reminder_sent=False
    ).select_related('user', 'category')
    
    sent_count = 0
    for task in upcoming_tasks:
        if task.user.profile.email_notifications and task.user.email:
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
                task.save()
                sent_count += 1
            except Exception as e:
                print(f"Failed to send email to {task.user.email}: {str(e)}")
    
    return f"Sent {sent_count} deadline reminders"


@shared_task
def send_daily_task_summary():
    """
    Send daily task summary to all users with email notifications enabled
    """
    users = User.objects.filter(profile__email_notifications=True).prefetch_related('tasks')
    
    sent_count = 0
    for user in users:
        if not user.email:
            continue
        
        # Get user's task statistics
        pending_tasks = user.tasks.filter(status='pending').count()
        in_progress_tasks = user.tasks.filter(status='in_progress').count()
        completed_today = user.tasks.filter(
            status='completed',
            completed_at__date=timezone.now().date()
        ).count()
        overdue_tasks = user.tasks.filter(
            deadline__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).count()
        
        # Only send if user has active tasks
        if pending_tasks + in_progress_tasks + overdue_tasks == 0:
            continue
        
        subject = 'Daily Task Summary'
        message = f"""
Hello {user.get_full_name() or user.username},

Here's your daily task summary:

📋 Pending Tasks: {pending_tasks}
🔄 In Progress: {in_progress_tasks}
✅ Completed Today: {completed_today}
⚠️ Overdue Tasks: {overdue_tasks}

"""
        
        # Add overdue task details if any
        if overdue_tasks > 0:
            message += "\nOverdue Tasks:\n"
            overdue_task_list = user.tasks.filter(
                deadline__lt=timezone.now(),
                status__in=['pending', 'in_progress']
            )[:5]  # Limit to 5 tasks
            
            for task in overdue_task_list:
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
            print(f"Failed to send email to {user.email}: {str(e)}")
    
    return f"Sent {sent_count} daily summaries"


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

