def lecture_attendance_notification(sender, instance, created, **kwargs):
    """Create a notification for the student user when attendance is recorded for a lecture."""
    try:
        # Resolve student user and lecture
        student = instance.student
        user = getattr(student, 'user', None)
        if not user:
            return

        lecture = getattr(instance, 'lecture', None)
        if lecture:
            lecture_title = lecture.title
            lecture_date = lecture.date
            school_class = lecture.school_class
        else:
            lecture_title = 'Lecture'
            lecture_date = None
            school_class = None

        status = 'present' if instance.present else 'absent'
        message = f"Attendance for '{lecture_title}' on {lecture_date} marked as {status}."

        Notification.objects.create(
            recipient=user,
            message=message,
            recipient_class=school_class if school_class is not None else None,
        )
    except Exception:
        # Don't let notification failures break the main flow
        return
