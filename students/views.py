from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Student, Attendance, Grade
from .forms import StudentForm, AttendanceForm, GradeForm
from finance.models import FeePayment
from notifications.models import Notification
from django.http import JsonResponse
from library.models import BorrowRecord, Book
from django.db import models
from django.utils import timezone
from django.contrib.auth.decorators import login_required
@login_required
def student_dashboard(request):
    # Mark notification as read (AJAX)
    if request.method == "POST" and request.POST.get("action") == "mark_read":
        notif_id = request.POST.get("notif_id")
        try:
            notif = Notification.objects.get(id=notif_id, recipient=request.user)
            notif.read = True
            notif.save()
            return JsonResponse({"success": True})
        except Notification.DoesNotExist:
            return JsonResponse({"success": False, "error": "Notification not found."})

    # Send message (AJAX)
    if request.method == "POST" and request.POST.get("action") == "send_message":
        message = request.POST.get("message")
        # Optionally, allow sending to staff/teachers
        # For now, send to admin
        from users.models import User
        admin = User.objects.filter(role="admin").first()
        if admin and message:
            Notification.objects.create(recipient=admin, message=f"Student message: {message}")
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "error": "Admin not found or message empty."})
    # Class & Subject Info
    from classes.models import Subject, SchoolClass
    from teachers.models import Timetable, Teacher
    subjects = []
    timetable = []
    teachers = []
    if student.school_class:
        subjects = Subject.objects.filter(schoolclass=student.school_class) if hasattr(Subject, 'schoolclass') else []
        timetable = Timetable.objects.filter(school_class=student.school_class).order_by('day', 'period')
        teachers = Teacher.objects.filter(teacher_profile__subjects__in=subjects).distinct()

    context.update({
        'subjects': subjects,
        'timetable': timetable,
        'teachers': teachers,
    })
    # Fees & Finance
    from finance.models import FeePayment, Invoice
    payments = FeePayment.objects.filter(student=student).order_by('-date_paid')
    invoices = Invoice.objects.filter(student=student).order_by('-issued_date')

    context.update({
        'payments': payments,
        'invoices': invoices,
    })
    # Academic results for chart (last 6 terms)
    grades = Grade.objects.filter(student=student).order_by('-year', '-term')[:30]
    grade_labels = []
    grade_data = []
    for g in reversed(grades):
        label = f"{g.term} {g.year}"
        grade_labels.append(label)
        grade_data.append(float(g.score))

    # GPA calculation (simple average)
    gpa = round(sum(grade_data) / len(grade_data), 2) if grade_data else 0

    context.update({
        'grade_labels': grade_labels,
        'grade_data': grade_data,
        'gpa': gpa,
    })
    # Get student profile
    student = getattr(request.user, 'student_profile', None)
    if not student:
        return redirect('/')

    # Metrics
    subjects_count = 0
    attendance_percent = 0
    latest_exam_score = 0
    fee_balance = 0
    notifications = []

    # Subjects
    if student.school_class:
        subjects_count = student.school_class.subjects.count() if hasattr(student.school_class, 'subjects') else 0

    # Attendance
    total_days = Attendance.objects.filter(student=student).count()
    present_days = Attendance.objects.filter(student=student, present=True).count()
    attendance_percent = int((present_days / total_days) * 100) if total_days else 0

    # Latest Exam Score
    latest_grade = Grade.objects.filter(student=student).order_by('-year', '-term').first()
    latest_exam_score = latest_grade.score if latest_grade else 0

    # Fee Balance
    paid = FeePayment.objects.filter(student=student).aggregate(total=models.Sum('amount'))['total'] or 0
    # Assume fee structure for class
    fee_struct = None
    if student.school_class:
        from finance.models import FeeStructure
        fee_struct = FeeStructure.objects.filter(school_class=student.school_class).first()
    total_fee = fee_struct.amount if fee_struct else 0
    fee_balance = total_fee - paid


    # Library / Resources
    borrowed_books = BorrowRecord.objects.filter(student=student, returned=False).select_related('book').order_by('due_date')
    downloadable_materials = []
    try:
        # If you have a model for materials, replace this with actual query
        # For now, placeholder: downloadable_materials = Material.objects.filter(student=student)
        pass
    except Exception:
        downloadable_materials = []

    # Notifications
    try:
        notifications = Notification.objects.filter(recipient=request.user).order_by('-sent_at')[:10]
    except Exception:
        notifications = []

    # Attendance data for chart (last 12 months)
    from collections import OrderedDict
    import datetime
    today = datetime.date.today()
    months = [(today.replace(day=1) - datetime.timedelta(days=30*i)).strftime('%b %Y') for i in reversed(range(12))]
    attendance_by_month = OrderedDict((m, 0) for m in months)
    for record in Attendance.objects.filter(student=student, present=True):
        month_label = record.date.strftime('%b %Y')
        if month_label in attendance_by_month:
            attendance_by_month[month_label] += 1

    context = {
        'user': request.user,
        'student_profile': student,
        'subjects_count': subjects_count,
        'attendance_percent': attendance_percent,
        'latest_exam_score': latest_exam_score,
        'fee_balance': fee_balance,
        'notifications': notifications,
        'attendance_labels': list(attendance_by_month.keys()),
        'attendance_data': list(attendance_by_month.values()),
        'borrowed_books': borrowed_books,
        'downloadable_materials': downloadable_materials,
    }
    return render(request, 'users/dashboard_student.html', context)
from django.contrib.auth.decorators import login_required

@login_required
def student_list(request):
    students = Student.objects.all()
    return render(request, "students/list.html", {"students": students})

@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, "students/detail.html", {"student": student})

@login_required
def student_create(request):
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save()
            return redirect("students:detail", pk=student.pk)
    else:
        form = StudentForm()
    return render(request, "students/form.html", {"form": form})

@login_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            return redirect("students:detail", pk=student.pk)
    else:
        form = StudentForm(instance=student)
    return render(request, "students/form.html", {"form": form})

@login_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.delete()
    return redirect("students:list")

@login_required
def attendance_list(request):
    records = Attendance.objects.select_related('student').all().order_by('-date')
    return render(request, 'students/attendance_list.html', {'records': records})

@login_required
def grade_list(request):
    grades = Grade.objects.select_related('student').all()
    return render(request, 'students/grade_list.html', {'grades': grades})


@login_required
def assignments_list(request):
    student = getattr(request.user, 'student_profile', None)
    if not student:
        return redirect('login')
    assignments = []
    if student.school_class:
        assignments = student.school_class.assignments.order_by('due_date')
    return render(request, 'students/assignments_list.html', {'assignments': assignments})


@login_required
def assignment_detail(request, pk):
    from .models import Assignment, Submission
    assignment = get_object_or_404(Assignment, pk=pk)
    student = getattr(request.user, 'student_profile', None)
    submission = Submission.objects.filter(assignment=assignment, student=student).first()

    if request.method == 'POST' and request.FILES.get('submission_file'):
        file = request.FILES['submission_file']
        if submission:
            submission.file = file
            submission.submitted_at = timezone.now()
            submission.save()
        else:
            Submission.objects.create(assignment=assignment, student=student, file=file)
        return redirect('students:assignments')

    return render(request, 'students/assignment_detail.html', {'assignment': assignment, 'submission': submission})


@login_required
def materials_list(request):
    student = getattr(request.user, 'student_profile', None)
    materials = []
    if student and student.school_class:
        materials = student.school_class.materials.order_by('-uploaded_at')
    return render(request, 'students/materials_list.html', {'materials': materials})


@login_required
def inbox(request):
    user = request.user
    messages = user.received_messages.order_by('-sent_at')[:50]
    return render(request, 'students/inbox.html', {'messages': messages})


@login_required
def send_message(request):
    from users.models import User
    from .models import Message
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient')
        subject = request.POST.get('subject')
        body = request.POST.get('body')
        try:
            recipient = User.objects.get(pk=recipient_id)
            Message.objects.create(sender=request.user, recipient=recipient, subject=subject, body=body)
            return redirect('students:inbox')
        except Exception:
            pass
    users = User.objects.exclude(pk=request.user.pk)
    return render(request, 'students/send_message.html', {'users': users})
