from students.models import Student as StudentModel, Attendance as AttendanceModel, Grade as GradeModel
from teachers.models import Teacher as TeacherModel
from users.models import User
from finance.models import FeePayment
from notifications.models import Notification
from classes.models import SchoolClass
from django.db.models import Count, Avg, Sum
from django.contrib.auth.decorators import login_required
# Headteacher Dashboard
@login_required
def dashboard_headteacher(request):
    from django.utils import timezone
    from datetime import datetime, timedelta
    from django.db.models import Q, F
    
    # Enhanced Metrics
    total_students = StudentModel.objects.count()
    total_teachers = TeacherModel.objects.count()
    total_staff = User.objects.filter(role='non_teaching').count()
    
    # Calculate attendance percentage
    total_attendance_records = AttendanceModel.objects.count()
    present_records = AttendanceModel.objects.filter(present=True).count()
    attendance_overview = (present_records * 100 // total_attendance_records) if total_attendance_records > 0 else 0
    
    # Fee collection metrics
    fee_collection = FeePayment.objects.aggregate(total=Sum('amount'))['total'] or 0
    pending_fees = FeePayment.objects.filter(status='pending').aggregate(total=Sum('amount'))['total'] or 0
    
    # Recent notifications
    notifications = Notification.objects.order_by('-created')[:5]
    
    # Student analytics
    students = StudentModel.objects.all()
    filter_class = request.GET.get('class')
    filter_section = request.GET.get('section')
    filter_year = request.GET.get('year')
    
    if filter_class:
        students = students.filter(school_class__name=filter_class)
    if filter_section:
        students = students.filter(school_class__section__name=filter_section)
    if filter_year:
        students = students.filter(admission_year=filter_year)
    
    # Student performance analytics
    low_attendance_students = []
    failing_grades_students = []
    top_performers_students = []
    
    for student in students:
        # Calculate attendance percentage for each student
        student_attendance = AttendanceModel.objects.filter(student=student)
        if student_attendance.exists():
            present_count = student_attendance.filter(present=True).count()
            total_count = student_attendance.count()
            attendance_percentage = (present_count * 100) // total_count
            if attendance_percentage < 75:
                low_attendance_students.append(student)
        
        # Check for failing grades
        if GradeModel.objects.filter(student=student, score__lt=40).exists():
            failing_grades_students.append(student)
        
        # Check for top performers
        if GradeModel.objects.filter(student=student, score__gte=85).exists():
            top_performers_students.append(student)
    
    # Teacher analytics
    teachers = TeacherModel.objects.all()
    active_teachers = teachers.filter(status='Active').count()
    on_leave_teachers = teachers.filter(status='On Leave').count()
    
    # Class analytics
    classes = SchoolClass.objects.all()
    class_performance_data = []
    for school_class in classes:
        class_students = students.filter(school_class=school_class)
        if class_students.exists():
            avg_attendance = 0
            if AttendanceModel.objects.filter(student__in=class_students).exists():
                total_attendance = AttendanceModel.objects.filter(student__in=class_students).count()
                present_attendance = AttendanceModel.objects.filter(student__in=class_students, present=True).count()
                avg_attendance = (present_attendance * 100) // total_attendance if total_attendance > 0 else 0
            
            class_performance_data.append({
                'class': school_class,
                'student_count': class_students.count(),
                'attendance_percentage': avg_attendance
            })
    
    # Recent activities
    recent_attendance = AttendanceModel.objects.select_related('student').order_by('-date')[:10]
    recent_grades = GradeModel.objects.select_related('student').order_by('-id')[:10]
    
    # Chart data for analytics
    # Attendance trend (last 30 days)
    attendance_chart_data = []
    performance_chart_data = []
    enrollment_chart_data = []
    
    # Generate attendance trend data
    today = timezone.now().date()
    for i in range(29, -1, -1):
        date = today - timedelta(days=i)
        day_attendance = AttendanceModel.objects.filter(date=date)
        total_day = day_attendance.count()
        present_day = day_attendance.filter(present=True).count()
        percentage = (present_day * 100) // total_day if total_day > 0 else 0
        
        attendance_chart_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'percentage': percentage
        })
    
    # Performance data by class
    for school_class in classes:
        class_students = students.filter(school_class=school_class)
        if class_students.exists():
            avg_score = GradeModel.objects.filter(student__in=class_students).aggregate(avg=Avg('score'))['avg'] or 0
            performance_chart_data.append({
                'class': school_class.name,
                'avg_score': float(avg_score)
            })
    
    # Enrollment trend (monthly for last 12 months)
    current_date = timezone.now().date()
    for i in range(11, -1, -1):
        month_start = current_date.replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        monthly_enrollment = StudentModel.objects.filter(
            enrollment_date__gte=month_start,
            enrollment_date__lt=month_end
        ).count()
        
        enrollment_chart_data.append({
            'month': month_start.strftime('%Y-%m'),
            'enrollment': monthly_enrollment
        })

    context = {
        'user': request.user,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_staff': total_staff,
        'active_teachers': active_teachers,
        'on_leave_teachers': on_leave_teachers,
        'attendance_overview': attendance_overview,
        'fee_collection': fee_collection,
        'pending_fees': pending_fees,
        'notifications': notifications,
        'attendance_chart_data': attendance_chart_data,
        'performance_chart_data': performance_chart_data,
        'enrollment_chart_data': enrollment_chart_data,
        'students': students,
        'low_attendance_students': low_attendance_students,
        'failing_grades_students': failing_grades_students,
        'top_performers_students': top_performers_students,
        'teachers': teachers,
        'classes': classes,
        'class_performance_data': class_performance_data,
        'recent_attendance': recent_attendance,
        'recent_grades': recent_grades,
    }
    return render(request, 'school/dashboard_headteacher.html', context)
from django.shortcuts import render, get_object_or_404, redirect
from .models import Student, Teacher, Course, SchoolProfile
from django.db import OperationalError
from .forms import StudentForm, TeacherForm, CourseForm
from django.contrib.auth.decorators import login_required
from .forms import AttendanceForm, MarkForm
from .models import Attendance, Exam, Mark
from django.http import JsonResponse
from django.utils import timezone
from .models import BookLoan, Fee
from .forms import BookLoanForm, FeePaymentForm


def index(request):
    students = Student.objects.all()
    return render(request, "school/student_list.html", {"students": students})


def landing(request):
    """Render the public landing page using the first SchoolProfile entry."""
    try:
        school = SchoolProfile.objects.first()
    except OperationalError:
        # Database tables might not exist yet (e.g., during initial setup)
        school = SchoolProfile(name="Our School")
    # Provide a minimal fallback if no profile exists
    if school is None:
        school = SchoolProfile(name="Our School")
    return render(request, "landing.html", {"school": school})


def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, "school/student_detail.html", {"student": student})


def student_create(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            return redirect("school:student_detail", pk=student.pk)
    else:
        form = StudentForm()
    return render(request, "school/student_form.html", {"form": form})


def teacher_list(request):
    teachers = Teacher.objects.all()
    return render(request, "school/teacher_list.html", {"teachers": teachers})


def teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    return render(request, "school/teacher_detail.html", {"teacher": teacher})


def teacher_create(request):
    if request.method == "POST":
        form = TeacherForm(request.POST)
        if form.is_valid():
            teacher = form.save()
            return redirect("school:teacher_detail", pk=teacher.pk)
    else:
        form = TeacherForm()
    return render(request, "school/teacher_form.html", {"form": form})


def course_list(request):
    courses = Course.objects.all()
    return render(request, "school/course_list.html", {"courses": courses})


def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    return render(request, "school/course_detail.html", {"course": course})


def course_create(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            return redirect("school:course_detail", pk=course.pk)
    else:
        form = CourseForm()
    return render(request, "school/course_form.html", {"form": form})


@login_required
def dashboard(request):
    user = request.user
    role = getattr(user, "role", "admin") if user.is_authenticated else "guest"
    context = {}
    if user.is_superuser or user.is_staff or role == "admin":
        template = "school/dashboard_admin.html"
        # Provide admin dashboard context
        from .models import Student, Teacher, Attendance, Exam
        from django.utils import timezone
        students_count = Student.objects.count()
        teachers_count = Teacher.objects.count()
        today = timezone.localdate()
        attendance_today = Attendance.objects.filter(date=today).count()
        upcoming_exams = Exam.objects.filter(date__gte=today).count()
        context = {
            'students_count': students_count,
            'teachers_count': teachers_count,
            'attendance_today': attendance_today,
            'upcoming_exams': upcoming_exams,
        }
    elif role == "teacher":
        template = "school/dashboard_teacher.html"
        # Provide teacher dashboard context (add more as needed)
        from .models import Teacher, Attendance, Exam
        teacher = getattr(user, 'teacher_profile', None)
        classes = teacher.subjects.all() if teacher else []
        attendance_records = Attendance.objects.filter(student__school_class__in=classes) if teacher else []
        upcoming_exams = Exam.objects.filter(date__gte=timezone.localdate())
        context = {
            'teacher': teacher,
            'classes': classes,
            'attendance_records': attendance_records,
            'upcoming_exams': upcoming_exams,
        }
    elif role == "student":
        template = "school/dashboard_student.html"
        # Provide student dashboard context (add more as needed)
        from .models import Student, Attendance, Exam
        student = Student.objects.filter(user=user).first() if user.is_authenticated else None
        attendance_records = Attendance.objects.filter(student=student) if student else []
        upcoming_exams = Exam.objects.filter(date__gte=timezone.localdate())
        context = {
            'student': student,
            'attendance_records': attendance_records,
            'upcoming_exams': upcoming_exams,
        }
    else:
        template = "school/dashboard_student.html"
    return render(request, template, context)


@login_required
def admin_summary(request):
    # simple counts
    students_count = Student.objects.count()
    teachers_count = Teacher.objects.count()
    today = timezone.localdate()
    attendance_today = Attendance.objects.filter(date=today).count()
    upcoming_exams = Exam.objects.filter(date__gte=today).count()
    return render(request, 'school/dashboard_admin.html', {
        'students_count': students_count,
        'teachers_count': teachers_count,
        'attendance_today': attendance_today,
        'upcoming_exams': upcoming_exams,
    })


@login_required
def summary_chart_data(request):
    # return simple last-7-days attendance counts
    today = timezone.localdate()
    labels = []
    data = []
    for i in range(6, -1, -1):
        d = today - timezone.timedelta(days=i)
        labels.append(d.strftime('%Y-%m-%d'))
        data.append(Attendance.objects.filter(date=d).count())
    return JsonResponse({'labels': labels, 'data': data})


@login_required
def attendance_list(request):
    records = Attendance.objects.select_related('student').all().order_by('-date')
    return render(request, 'school/attendance_list.html', {'records': records})


@login_required
def attendance_create(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('school:attendance_list')
    else:
        form = AttendanceForm()
    return render(request, 'school/attendance_form.html', {'form': form})


@login_required
def marks_list(request):
    marks = Mark.objects.select_related('student', 'exam').all().order_by('-exam__date')
    return render(request, 'school/marks_list.html', {'marks': marks})


@login_required
def mark_create(request):
    if request.method == 'POST':
        form = MarkForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('school:marks_list')
    else:
        form = MarkForm()
    return render(request, 'school/mark_form.html', {'form': form})


@login_required
def bookloans_list(request):
    loans = BookLoan.objects.select_related('book', 'student').all().order_by('-checkout_date')
    return render(request, 'school/bookloan_list.html', {'loans': loans})


@login_required
def bookloan_create(request):
    if request.method == 'POST':
        form = BookLoanForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('school:bookloan_list')
    else:
        form = BookLoanForm()
    return render(request, 'school/bookloan_form.html', {'form': form})


@login_required
def bookloan_return(request, pk):
    loan = get_object_or_404(BookLoan, pk=pk)
    if not loan.returned:
        loan.mark_returned()
    return redirect('school:bookloan_list')


@login_required
def fees_list(request):
    fees = Fee.objects.select_related('student').all().order_by('due_date')
    return render(request, 'school/fees_list.html', {'fees': fees})


@login_required
def fee_toggle_paid(request, pk):
    fee = get_object_or_404(Fee, pk=pk)
    fee.paid = not fee.paid
    fee.save()
    return redirect('school:fees_list')
