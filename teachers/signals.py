from django.db.models.signals import post_save
from django.dispatch import receiver
from students.models import Submission
from .models import LeaveRequest, SubstituteAssignment
from notifications.models import Notification


@receiver(post_save, sender=Submission)
def notify_on_submission_graded(sender, instance, created, **kwargs):
    # Notify student when their submission is graded
    try:
        if instance.marks_obtained is not None:
            recipient = instance.student.user
            message = f"Your submission for '{instance.assignment.title}' was graded: {instance.marks_obtained}."
            if instance.feedback:
                message += f" Feedback: {instance.feedback}"
            Notification.objects.create(recipient=recipient, message=message)
    except Exception:
        # avoid breaking save on notification errors
        pass


@receiver(post_save, sender=LeaveRequest)
def notify_on_leave_approved(sender, instance, created, **kwargs):
    # Notify teacher when leave request status changes to Approved
    try:
        if instance.status == 'Approved':
            recipient = instance.teacher.user
            message = f"Your leave from {instance.start_date} to {instance.end_date} has been approved."
            Notification.objects.create(recipient=recipient, message=message)
    except Exception:
        pass


@receiver(post_save, sender=SubstituteAssignment)
def notify_on_substitute_assigned(sender, instance, created, **kwargs):
    try:
        if created:
            # notify substitute
            if instance.substitute_teacher and instance.substitute_teacher.user:
                recipient = instance.substitute_teacher.user
                message = f"You have been assigned as substitute for {instance.original_teacher} on {instance.date} (Class: {instance.school_class})."
                Notification.objects.create(recipient=recipient, message=message)
            # notify original teacher
            if instance.original_teacher and instance.original_teacher.user:
                recipient = instance.original_teacher.user
                message = f"A substitute ({instance.substitute_teacher}) has been assigned for your class on {instance.date}."
                Notification.objects.create(recipient=recipient, message=message)
    except Exception:
        pass
