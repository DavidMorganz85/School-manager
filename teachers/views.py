from django.contrib.auth.decorators import login_required
@login_required
def teacher_dashboard(request):
    teacher = getattr(request.user, 'teacher_profile', None)
    if not teacher:
        return redirect('/')

    # Metrics
    total_classes = teacher.subjects.values('schoolclass').distinct().count() if hasattr(teacher.subjects.model, 'schoolclass') else 0
    total_subjects = teacher.subjects.count()
    from students.models import Student, Grade, Attendance
    students = Student.objects.filter(school_class__in=teacher.subjects.values('schoolclass')) if hasattr(teacher.subjects.model, 'schoolclass') else Student.objects.none()
    total_students = students.count()
    pending_marks = Grade.objects.filter(subject__in=teacher.subjects.all(), score=None).count()

    # Upcoming exams/lessons (placeholder)
    upcoming_exams = []

    # Notifications (placeholder)
    notifications = []

    # Profile
    profile = teacher

    # Classes & Students
    classes = teacher.subjects.values_list('schoolclass', flat=True).distinct() if hasattr(teacher.subjects.model, 'schoolclass') else []

    # Attendance
    attendance_records = Attendance.objects.filter(student__in=students)

    # Academic Results
    grades = Grade.objects.filter(student__in=students)

    # Timetable
    timetables = Timetable.objects.filter(teacher=teacher)

    # Resources/Library (placeholder)
    resources = []

    context = {
        'user': request.user,
        'profile': profile,
        'total_classes': total_classes,
        'total_subjects': total_subjects,
        'total_students': total_students,
        'pending_marks': pending_marks,
        'upcoming_exams': upcoming_exams,
        'notifications': notifications,
        'classes': classes,
        'students': students,
        'attendance_records': attendance_records,
        'grades': grades,
        'timetables': timetables,
        'resources': resources,
    }
    return render(request, 'users/dashboard_teacher.html', context)
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
import io
from xhtml2pdf import pisa
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Teacher, Timetable, Exam, Assessment, SubjectGroup
from .forms import LeaveRequestForm, LessonPlanForm, TeacherAttendanceForm
from .models import LeaveRequest, TeacherAttendance, LessonPlan, SubstituteAssignment
from django.utils import timezone
from notifications.models import Notification


@login_required
def leave_request_create(request):
    teacher = getattr(request.user, 'teacher_profile', None)
    if not teacher:
        return redirect('/')

    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            lr = form.save(commit=False)
            lr.teacher = teacher
            lr.save()
            messages.success(request, 'Leave request submitted')
            return redirect(reverse('teachers:leave_requests'))
    else:
        form = LeaveRequestForm()
    return render(request, 'teachers/leave_request_form.html', {'form': form})


@login_required
def leave_request_list(request):
    teacher = getattr(request.user, 'teacher_profile', None)
    if request.user.is_staff:
        # admins can view all
        leaves = LeaveRequest.objects.all().order_by('-created_at')
    elif teacher:
        leaves = LeaveRequest.objects.filter(teacher=teacher).order_by('-created_at')
    else:
        return redirect('/')
    return render(request, 'teachers/leave_request_list.html', {'leaves': leaves})


@login_required
def leave_request_approve(request, pk):
    # approval should be done by staff or HOD
    if not request.user.is_staff:
        messages.error(request, 'Permission denied')
        return redirect(reverse('teachers:leave_requests'))
    lr = get_object_or_404(LeaveRequest, pk=pk)
    action = request.GET.get('action')
    if action == 'approve':
        lr.status = 'Approved'
        lr.approved_by = request.user
        lr.approved_at = timezone.now()
        lr.save()
        # create notification for the teacher
        try:
            if lr.teacher and getattr(lr.teacher, 'user', None):
                Notification.objects.create(recipient=lr.teacher.user, message=f"Your leave request from {lr.start_date} to {lr.end_date} has been approved.")
        except Exception:
            pass
        messages.success(request, 'Leave approved')
    elif action == 'reject':
        lr.status = 'Rejected'
        lr.approved_by = request.user
        lr.approved_at = timezone.now()
        lr.save()
        try:
            if lr.teacher and getattr(lr.teacher, 'user', None):
                Notification.objects.create(recipient=lr.teacher.user, message=f"Your leave request from {lr.start_date} to {lr.end_date} has been rejected.")
        except Exception:
            pass
        messages.success(request, 'Leave rejected')
    return redirect(reverse('teachers:leave_requests'))


@login_required
def teacher_attendance_log(request):
    teacher = getattr(request.user, 'teacher_profile', None)
    if not teacher:
        return redirect('/')
    if request.method == 'POST':
        form = TeacherAttendanceForm(request.POST)
        if form.is_valid():
            att = form.save(commit=False)
            att.teacher = teacher
            att.save()
            messages.success(request, 'Attendance recorded')
            return redirect(reverse('teachers:attendance_log'))
    else:
        form = TeacherAttendanceForm(initial={'date': timezone.now().date()})
    records = TeacherAttendance.objects.filter(teacher=teacher).order_by('-date')[:30]
    return render(request, 'teachers/attendance_log.html', {'form': form, 'records': records})


@login_required
def lessonplan_upload(request):
    teacher = getattr(request.user, 'teacher_profile', None)
    if not teacher:
        return redirect('/')
    if request.method == 'POST':
        form = LessonPlanForm(request.POST, request.FILES)
        if form.is_valid():
            lp = form.save(commit=False)
            lp.teacher = teacher
            lp.save()
            messages.success(request, 'Lesson plan uploaded')
            return redirect(reverse('teachers:lessonplans'))
    else:
        form = LessonPlanForm()
    plans = LessonPlan.objects.filter(teacher=teacher).order_by('-uploaded_at')
    return render(request, 'teachers/lessonplans_list.html', {'form': form, 'plans': plans})
from students.models import Student, Promotion, StudentArchive, SubjectCombination
from classes.models import Level, Subject, Department
from django.db import models
# Student progression and archiving
from students.models import Promotion, StudentArchive, SubjectCombination
# Student progression view
@login_required
def promote_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        to_level_id = request.POST.get("to_level")
        to_level = Level.objects.get(pk=to_level_id)
        Promotion.objects.create(student=student, from_level=student.level, to_level=to_level, promoted_by=request.user)
        student.level = to_level
        student.promoted = True
        student.save()
        return redirect("students:detail", pk=student.pk)
    levels = Level.objects.all()
    return render(request, "students/promote_form.html", {"student": student, "levels": levels})

# Archive student view
@login_required
def archive_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        reason = request.POST.get("reason")
        StudentArchive.objects.create(student=student, reason=reason)
        return redirect("students:list")
    return render(request, "students/archive_form.html", {"student": student})

# Subject combination validation for A-Level electives
@login_required
def validate_subject_combination(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        stream = request.POST.get("stream")
        subject_ids = request.POST.getlist("subjects")
        subjects = Subject.objects.filter(pk__in=subject_ids)
        # Example validation: Science stream must have Physics, Chemistry, Biology, Mathematics
        valid = True
        if stream == "Science":
            required = set(["Physics", "Chemistry", "Biology", "Mathematics"])
            selected = set(subjects.values_list("name", flat=True))
            valid = required.issubset(selected)
        elif stream == "Arts":
            required = set(["History", "Economics", "Literature"])
            selected = set(subjects.values_list("name", flat=True))
            valid = required.issubset(selected)
        if valid:
            SubjectCombination.objects.create(student=student, stream=stream)
            student.subjects.set(subjects)
            student.save()
            return redirect("students:detail", pk=student.pk)
        else:
            error = "Invalid subject combination for selected stream."
            return render(request, "students/subject_combination_form.html", {"student": student, "error": error, "subjects": Subject.objects.all()})
    return render(request, "students/subject_combination_form.html", {"student": student, "subjects": Subject.objects.all()})

# Department, HOD, and admin management features
@login_required
def department_dashboard(request):
    departments = Department.objects.all()
    return render(request, "classes/department_dashboard.html", {"departments": departments})

@login_required
def hod_dashboard(request):
    hod = getattr(request.user, 'teacher_profile', None)
    if not hod or not hod.is_hod:
        return redirect("/")
    department = hod.department
    teachers = Teacher.objects.filter(department=department)
    subjects = department.subjects.all() if department else []
    return render(request, "users/dashboard_hod.html", {"hod": hod, "department": department, "teachers": teachers, "subjects": subjects})

@login_required
def admin_dashboard(request):
    # Full school academic overview
    teachers = Teacher.objects.all()
    students = Student.objects.all()
    departments = Department.objects.all()
    return render(request, "users/dashboard_admin.html", {"teachers": teachers, "students": students, "departments": departments})
from .forms import TeacherForm, TimetableForm
from django.contrib.auth.decorators import login_required

# --- Teacher assignment & grading views ---
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from students.models import Assignment, Submission
from .forms import AssignmentForm, GradeForm


@login_required
def teacher_assignments_list(request):
    # only teachers can access
    teacher = getattr(request.user, 'teacher_profile', None)
    if not teacher:
        return redirect('/')

    # show assignments created by this teacher
    assignments = Assignment.objects.filter(teacher=teacher).order_by('-created_at')
    return render(request, 'teachers/assignments_list.html', {'assignments': assignments, 'teacher': teacher})


@login_required
def teacher_create_assignment(request):
    teacher = getattr(request.user, 'teacher_profile', None)
    if not teacher:
        return redirect('/')

    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.teacher = teacher
            assignment.save()
            messages.success(request, 'Assignment created successfully')
            return redirect(reverse('teachers:assignments_list'))
    else:
        form = AssignmentForm()
    return render(request, 'teachers/create_assignment.html', {'form': form})


@login_required
def teacher_submissions_list(request, assignment_id):
    teacher = getattr(request.user, 'teacher_profile', None)
    if not teacher:
        return redirect('/')

    assignment = get_object_or_404(Assignment, pk=assignment_id)
    # ensure teacher owns this assignment or is staff
    if assignment.teacher != teacher and not request.user.is_staff:
        messages.error(request, 'Permission denied')
        return redirect(reverse('teachers:assignments_list'))

    submissions = Submission.objects.filter(assignment=assignment).order_by('-submitted_at')
    return render(request, 'teachers/submissions_list.html', {'assignment': assignment, 'submissions': submissions})


@login_required
def teacher_grade_submission(request, assignment_id, submission_id):
    teacher = getattr(request.user, 'teacher_profile', None)
    if not teacher:
        return redirect('/')

    submission = get_object_or_404(Submission, pk=submission_id, assignment_id=assignment_id)
    assignment = submission.assignment
    if assignment.teacher != teacher and not request.user.is_staff:
        messages.error(request, 'Permission denied')
        return redirect(reverse('teachers:assignments_list'))

    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            submission.marks_obtained = form.cleaned_data['marks_obtained']
            submission.feedback = form.cleaned_data.get('feedback', '')
            submission.graded_by = teacher
            submission.save()
            # notify student
            try:
                student_user = getattr(submission.student, 'user', None)
                if student_user:
                    Notification.objects.create(recipient=student_user, message=f"Your submission for '{assignment.title}' was graded: {submission.marks_obtained}.")
            except Exception:
                pass
            messages.success(request, 'Submission graded')
            return redirect(reverse('teachers:assignment_submissions', args=[assignment.id]))
    else:
        form = GradeForm(initial={'marks_obtained': submission.marks_obtained, 'feedback': submission.feedback})

    return render(request, 'teachers/grade_submission.html', {'submission': submission, 'form': form, 'assignment': assignment})


@login_required
@require_POST
def teacher_grade_submission_ajax(request, assignment_id, submission_id):
    """AJAX endpoint to grade a submission. Returns JSON."""
    teacher = getattr(request.user, 'teacher_profile', None)
    if not teacher:
        return JsonResponse({'success': False, 'error': 'Not permitted'}, status=403)

    submission = get_object_or_404(Submission, pk=submission_id, assignment_id=assignment_id)
    assignment = submission.assignment
    if assignment.teacher != teacher and not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    form = GradeForm(request.POST)
    if form.is_valid():
        submission.marks_obtained = form.cleaned_data['marks_obtained']
        submission.feedback = form.cleaned_data.get('feedback', '')
        submission.graded_by = teacher
        submission.save()
        # notify student
        try:
            student_user = getattr(submission.student, 'user', None)
            if student_user:
                Notification.objects.create(recipient=student_user, message=f"Your submission for '{assignment.title}' was graded: {submission.marks_obtained}.")
        except Exception:
            pass
        return JsonResponse({'success': True, 'marks_obtained': submission.marks_obtained})
    else:
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
def teacher_list(request):
    teachers = Teacher.objects.all()
    return render(request, "teachers/list.html", {"teachers": teachers})

@login_required
def teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    return render(request, "teachers/detail.html", {"teacher": teacher})

@login_required
def teacher_create(request):
    if request.method == "POST":
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            teacher = form.save()
            return redirect("teachers:detail", pk=teacher.pk)
    else:
        @login_required
        def teacher_dashboard(request):
            teacher = getattr(request.user, 'teacher_profile', None)
            if not teacher:
                return redirect('/')

            from students.models import Student, Grade, Attendance
            # Metrics
            total_classes = teacher.subjects.values('schoolclass').distinct().count() if hasattr(teacher.subjects.model, 'schoolclass') else 0
            total_subjects = teacher.subjects.count()
            students = Student.objects.filter(school_class__in=teacher.subjects.values('schoolclass')) if hasattr(teacher.subjects.model, 'schoolclass') else Student.objects.none()
            total_students = students.count()
            pending_marks = Grade.objects.filter(subject__in=teacher.subjects.all(), score=None).count()

            # Exams assigned to teacher
            exams = Exam.objects.filter(subject__in=teacher.subjects.all(), stream__in=teacher.streams.all())
            assessments = Assessment.objects.filter(exam__in=exams)

            # Grade calculation (average per class/stream)
            class_averages = {}
            for school_class in teacher.classes.all():
                grades = Grade.objects.filter(student__school_class=school_class, subject__in=teacher.subjects.all())
                avg = grades.aggregate(models.Avg('score'))['score__avg'] if grades.exists() else None
                class_averages[school_class.name] = round(avg, 2) if avg else None

            stream_averages = {}
            for stream in teacher.streams.all():
                grades = Grade.objects.filter(student__stream=stream, subject__in=teacher.subjects.all())
                avg = grades.aggregate(models.Avg('score'))['score__avg'] if grades.exists() else None
                stream_averages[stream.name] = round(avg, 2) if avg else None

            # Result reports per student
            student_reports = []
            for student in students:
                grades = Grade.objects.filter(student=student)
                avg = grades.aggregate(models.Avg('score'))['score__avg'] if grades.exists() else None
                student_reports.append({
                    'student': student,
                    'average': round(avg, 2) if avg else None,
                    'grades': grades,
                })

            # Upcoming exams
            upcoming_exams = exams.filter(date__gte=models.functions.Now()).order_by('date')

            # Notifications (placeholder)
            notifications = []

            # Profile
            profile = teacher

            # Classes & Students
            classes = teacher.subjects.values_list('schoolclass', flat=True).distinct() if hasattr(teacher.subjects.model, 'schoolclass') else []

            # Attendance
            attendance_records = Attendance.objects.filter(student__in=students)

            # Academic Results
            grades = Grade.objects.filter(student__in=students)

            # Timetable
            timetables = Timetable.objects.filter(teacher=teacher)

            # Resources/Library (placeholder)
            resources = []

            context = {
                'user': request.user,
                'profile': profile,
                'total_classes': total_classes,
                'total_subjects': total_subjects,
                'total_students': total_students,
                'pending_marks': pending_marks,
                'upcoming_exams': upcoming_exams,
                'notifications': notifications,
                'classes': classes,
                'students': students,
                'attendance_records': attendance_records,
                'grades': grades,
                'timetables': timetables,
                'resources': resources,
                'exams': exams,
                'assessments': assessments,
                'class_averages': class_averages,
                'stream_averages': stream_averages,
                'student_reports': student_reports,
            }
            return render(request, 'users/dashboard_teacher.html', context)
