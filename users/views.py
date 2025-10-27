
from rest_framework import viewsets, permissions
from .models import User
from .serializers import UserSerializer

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test


@login_required
def dashboard(request):
    role = request.user.role
    sub_role = getattr(request.user, "sub_role", None)
    if role == "admin":
        return render(request, "users/dashboard_admin.html")
    if role == "headteacher":
        from classes.models import Department
        total_departments = Department.objects.count()
        departments = Department.objects.select_related('head').all()
        context = {
            'user': request.user,
            'total_departments': total_departments,
            'departments': departments,
        }
        return render(request, "users/dashboard_headteacher.html", context)
    if role == "deputy_headteacher":
        # Summary cards
        from students.models import Student, Attendance, Grade
        from teachers.models import Teacher
        from classes.models import SchoolClass, Section, Subject
        from exams.models import Exam, Mark
        from notifications.models import Notification
        from django.db.models import Avg, Count, Q
        total_students = Student.objects.count()
        total_teachers = Teacher.objects.count()
        total_classes = SchoolClass.objects.count()
        attendance_summary = Attendance.objects.filter(present=True).count()
        attendance_total = Attendance.objects.count()
        attendance_percent = int((attendance_summary / attendance_total) * 100) if attendance_total else 0
        upcoming_exams = Exam.objects.filter(date__gte=datetime.date.today()).count()
        upcoming_events = 0 # Placeholder, add event model if available

        # Classes overview
        classes = []
        for c in SchoolClass.objects.select_related('section').all():
            teacher = Subject.objects.filter(schoolclass=c).first().teacher if Subject.objects.filter(schoolclass=c).exists() else None
            class_attendance = Attendance.objects.filter(student__school_class=c, present=True).count()
            class_total = Attendance.objects.filter(student__school_class=c).count()
            class_attendance_percent = int((class_attendance / class_total) * 100) if class_total else 0
            class_performance = Grade.objects.filter(student__school_class=c).aggregate(avg=Avg('score'))['avg'] or 0
            needs_attention = class_attendance_percent < 75 or class_performance < 50
            classes.append({
                'name': c.name,
                'section': c.section.name if c.section else '',
                'teacher': teacher.user.get_full_name() if teacher and hasattr(teacher, 'user') else '',
                'attendance': class_attendance_percent,
                'performance': round(class_performance, 2),
                'needs_attention': needs_attention,
            })

        # Teachers overview
        teachers = []
        for t in Teacher.objects.all():
            subjects = ', '.join([s.name for s in t.subjects.all()])
            submissions = 'Lesson plans, attendance, grades' # Placeholder
            teachers.append({
                'name': t.user.get_full_name(),
                'subjects': subjects,
                'submissions': submissions,
            })

        # Students & academic reports
        students = []
        for s in Student.objects.select_related('school_class').all():
            attendance = Attendance.objects.filter(student=s, present=True).count()
            total_att = Attendance.objects.filter(student=s).count()
            attendance_percent = int((attendance / total_att) * 100) if total_att else 0
            grade = Grade.objects.filter(student=s).aggregate(avg=Avg('score'))['avg'] or 0
            discipline = 'Good' # Placeholder
            at_risk = attendance_percent < 75 or grade < 50
            students.append({
                'name': s.user.get_full_name(),
                'class': s.school_class.name if s.school_class else '',
                'attendance': attendance_percent,
                'grade': round(grade, 2),
                'discipline': discipline,
                'at_risk': at_risk,
            })

        # Exams & timetable
        exams = []
        for e in Exam.objects.select_related('school_class', 'subject').all():
            exams.append({
                'name': e.name,
                'class': e.school_class.name if e.school_class else '',
                'subject': e.subject.name if e.subject else '',
                'date': e.date,
            })

        # Notifications
        notifications = Notification.objects.filter(recipient=request.user).order_by('-sent_at')[:10]

        # Charts data
        attendance_labels = [c['name'] for c in classes]
        attendance_data = [c['attendance'] for c in classes]
        performance_labels = [c['name'] for c in classes]
        performance_data = [c['performance'] for c in classes]

        context = {
            'user': request.user,
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_classes': total_classes,
            'attendance_summary': attendance_percent,
            'upcoming_exams': upcoming_exams,
            'upcoming_events': upcoming_events,
            'classes': classes,
            'teachers': teachers,
            'students': students,
            'exams': exams,
            'notifications': notifications,
            'attendance_labels': attendance_labels,
            'attendance_data': attendance_data,
            'performance_labels': performance_labels,
            'performance_data': performance_data,
        }
        return render(request, "users/dashboard_deputy.html", context)
    if role == "director_of_studies":
        from students.models import Student, Attendance, Grade
        from teachers.models import Teacher
        from classes.models import SchoolClass, Section, Subject
        from exams.models import Exam, Mark
        from notifications.models import Notification
        from django.db.models import Avg, Count, Q
        import datetime
        # Summary cards
        total_classes = SchoolClass.objects.count()
        total_students = Student.objects.count()
        exams_scheduled = Exam.objects.filter(date__gte=datetime.date.today()).count()
        pending_marks = Mark.objects.filter(score__isnull=True).count()
        students_at_risk = Student.objects.filter(grade__score__lt=50).distinct().count()

        # Exams & Assessments
        exams = []
        for e in Exam.objects.select_related('school_class', 'subject').all():
            marks_status = 'Pending' if Mark.objects.filter(exam=e, score__isnull=True).exists() else 'Complete'
            exams.append({
                'name': e.name,
                'class': e.school_class.name if e.school_class else '',
                'subject': e.subject.name if e.subject else '',
                'date': e.date,
                'marks_status': marks_status,
            })

        # Results & Academic Reports
        results = []
        top_score = Grade.objects.aggregate(max=Avg('score'))['max'] or 0
        for g in Grade.objects.select_related('student', 'student__school_class').all():
            top_performer = g.score >= top_score
            at_risk = g.score < 50
            results.append({
                'student': g.student.user.get_full_name(),
                'class': g.student.school_class.name if g.student.school_class else '',
                'subject': g.subject,
                'score': g.score,
                'term': g.term,
                'year': g.year,
                'top_performer': top_performer,
                'at_risk': at_risk,
            })

        # Teacher Oversight
        teachers = []
        for t in Teacher.objects.all():
            submissions = 'Marks, lesson plans, assignments' # Placeholder
            teachers.append({
                'name': t.user.get_full_name(),
                'submissions': submissions,
            })

        # Class & Student Oversight
        classes = []
        for c in SchoolClass.objects.select_related('section').all():
            class_attendance = Attendance.objects.filter(student__school_class=c, present=True).count()
            class_total = Attendance.objects.filter(student__school_class=c).count()
            class_attendance_percent = int((class_attendance / class_total) * 100) if class_total else 0
            class_performance = Grade.objects.filter(student__school_class=c).aggregate(avg=Avg('score'))['avg'] or 0
            at_risk = Student.objects.filter(school_class=c, grade__score__lt=50).distinct().count()
            classes.append({
                'name': c.name,
                'attendance': class_attendance_percent,
                'performance': round(class_performance, 2),
                'at_risk': at_risk,
            })

        # Notifications
        notifications = Notification.objects.filter(recipient=request.user).order_by('-sent_at')[:10]

        # Charts data
        exam_perf_labels = [e['name'] for e in exams]
        exam_perf_data = [Grade.objects.filter(student__school_class__name=e['class']).aggregate(avg=Avg('score'))['avg'] or 0 for e in exams]
        att_perf_labels = [c['name'] for c in classes]
        att_perf_data = [c['attendance'] for c in classes]

        context = {
            'user': request.user,
            'total_classes': total_classes,
            'total_students': total_students,
            'exams_scheduled': exams_scheduled,
            'pending_marks': pending_marks,
            'students_at_risk': students_at_risk,
            'exams': exams,
            'results': results,
            'teachers': teachers,
            'classes': classes,
            'notifications': notifications,
            'exam_perf_labels': exam_perf_labels,
            'exam_perf_data': exam_perf_data,
            'att_perf_labels': att_perf_labels,
            'att_perf_data': att_perf_data,
        }
        return render(request, "users/dashboard_dos.html", context)
    if role == "hod":
        return render(request, "users/dashboard_hod.html")
    if role == "teacher":
        return render(request, "users/dashboard_teacher.html")
    if role == "student":
        return render(request, "users/dashboard_student.html")
    if role == "non_teaching":
        if sub_role == "accounts":
            from students.models import Student
            from finance.models import FeePayment, Invoice
            from notifications.models import Notification
            from django.db.models import Sum, Q
            import datetime
            # Summary cards
            total_fees_collected = FeePayment.objects.aggregate(total=Sum('amount'))['total'] or 0
            pending_fees = Invoice.objects.filter(paid=False).aggregate(total=Sum('total'))['total'] or 0
            total_students = Student.objects.count()
            recent_transactions = FeePayment.objects.order_by('-date_paid')[:5]

            # Monthly fee collection trends
            months = [(datetime.date.today().replace(day=1) - datetime.timedelta(days=30*i)).strftime('%b %Y') for i in reversed(range(6))]
            fee_collection_labels = months
            fee_collection_data = []
            for m in months:
                year, month = m.split(' ')
                month_num = datetime.datetime.strptime(month, '%b').month
                year_num = int(year)
                total = FeePayment.objects.filter(date_paid__year=year_num, date_paid__month=month_num).aggregate(total=Sum('amount'))['total'] or 0
                fee_collection_data.append(total)

            # Student fee management
            students = []
            for s in Student.objects.select_related('school_class').all():
                paid = FeePayment.objects.filter(student=s).aggregate(total=Sum('amount'))['total'] or 0
                fee_struct = None
                try:
                    from finance.models import FeeStructure
                    fee_struct = FeeStructure.objects.filter(school_class=s.school_class).first()
                except Exception:
                    fee_struct = None
                total_fee = fee_struct.amount if fee_struct else 0
                fee_balance = total_fee - paid
                students.append({
                    'name': s.user.get_full_name(),
                    'class': s.school_class.name if s.school_class else '',
                    'fee_balance': fee_balance,
                })

            # Reports
            reports = []
            for c in Student.objects.values('school_class__name').distinct():
                class_name = c['school_class__name']
                collected = FeePayment.objects.filter(student__school_class__name=class_name).aggregate(total=Sum('amount'))['total'] or 0
                outstanding = Invoice.objects.filter(student__school_class__name=class_name, paid=False).aggregate(total=Sum('total'))['total'] or 0
                reports.append({
                    'term_class': class_name,
                    'collected': collected,
                    'outstanding': outstanding,
                })

            # Notifications
            notifications = Notification.objects.filter(recipient=request.user).order_by('-sent_at')[:10]

            context = {
                'user': request.user,
                'total_fees_collected': total_fees_collected,
                'pending_fees': pending_fees,
                'total_students': total_students,
                'recent_transactions': recent_transactions.count(),
                'fee_collection_labels': fee_collection_labels,
                'fee_collection_data': fee_collection_data,
                'students': students,
                'reports': reports,
                'notifications': notifications,
            }
            return render(request, "users/dashboard_accounts.html", context)
        if sub_role == "welfare":
            return render(request, "users/dashboard_welfare.html")
        if sub_role == "cleaner":
            return render(request, "users/dashboard_cleaner.html")
        if sub_role == "it_support":
            return render(request, "users/dashboard_it.html")
        return render(request, "users/dashboard_non_teaching.html")
    return redirect("/")

# User management views for role assignment and deactivation
from django.contrib.auth import get_user_model
from .forms import UserRoleForm, UserDeactivateForm

def is_admin_or_headteacher(user):
    return user.is_authenticated and user.role in ["admin", "headteacher"]

@user_passes_test(is_admin_or_headteacher)
def assign_role(request, user_id):
    User = get_user_model()
    user = User.objects.get(pk=user_id)
    if request.method == "POST":
        form = UserRoleForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("/users/")
    else:
        form = UserRoleForm(instance=user)
    return render(request, "users/assign_role.html", {"form": form, "user": user})

@user_passes_test(is_admin_or_headteacher)
def deactivate_user(request, user_id):
    User = get_user_model()
    user = User.objects.get(pk=user_id)
    if request.method == "POST":
        form = UserDeactivateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("/users/")
    else:
        form = UserDeactivateForm(instance=user)
    return render(request, "users/deactivate_user.html", {"form": form, "user": user})


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
