from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SchoolClass
# Import the helper forms used by multiple views
from .forms import SchoolClassForm, AssignStudentsForm, PromoteStudentsForm
from django.http import HttpResponse
from students.models import Student
import csv


@login_required
def class_assign_students(request, pk):
    """Assign students to a class (simple bulk assign)."""
    school_class = get_object_or_404(SchoolClass, pk=pk)
    # only allow staff or class teacher
    if not (request.user.is_staff or getattr(request.user, 'teacher_profile', None) == school_class.class_teacher):
        messages.error(request, 'Permission denied')
        return redirect(reverse('classes:class_detail', args=[pk]))

    if request.method == 'POST':
        student_ids = request.POST.getlist('students')
        students = Student.objects.filter(id__in=student_ids)
        for s in students:
            s.school_class = school_class
            s.save()
        # update counts
        school_class.current_student_count = Student.objects.filter(school_class=school_class).count()
        school_class.save()
        messages.success(request, f'Assigned {students.count()} students to {school_class}')
        return redirect(reverse('classes:class_detail', args=[pk]))

    # show students not in this class
    available_students = Student.objects.filter(school_class__isnull=True)[:200]
    return render(request, 'classes/class_assign_students.html', {'class': school_class, 'students': available_students})


@login_required
def export_classes_csv(request):
    # simple CSV export of classes
    if not request.user.is_staff:
        messages.error(request, 'Permission denied')
        return redirect(reverse('classes:class_list'))

    classes_qs = SchoolClass.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="classes_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Level', 'Section', 'Teacher', 'Students', 'Capacity', 'Academic Year', 'Term'])
    for c in classes_qs:
        writer.writerow([c.id, c.name, str(c.level), c.section, str(c.class_teacher) if c.class_teacher else '', c.current_student_count, c.capacity, c.academic_year, c.term])
    return response


@login_required
def class_list(request):
    classes = SchoolClass.objects.all().order_by('level__name', 'name', 'section')
    return render(request, 'classes/class_list.html', {'classes': classes})


@login_required
def class_detail(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk)
    return render(request, 'classes/class_detail.html', {'class': school_class})


@login_required
def class_create(request):
    if request.method == 'POST':
        form = SchoolClassForm(request.POST)
        if form.is_valid():
            cls = form.save(commit=False)
            cls.created_by = request.user
            cls.save()
            messages.success(request, 'Class created')
            return redirect(reverse('classes:class_list'))
    else:
        form = SchoolClassForm()
    return render(request, 'classes/class_form.html', {'form': form})


@login_required
def class_edit(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk)
    if request.method == 'POST':
        form = SchoolClassForm(request.POST, instance=school_class)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class updated')
            return redirect(reverse('classes:class_detail', args=[school_class.id]))
    else:
        form = SchoolClassForm(instance=school_class)
    return render(request, 'classes/class_form.html', {'form': form, 'class': school_class})


@login_required
def class_delete(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk)
    if request.method == 'POST':
        school_class.delete()
        messages.success(request, 'Class deleted')
        return redirect(reverse('classes:class_list'))
    return render(request, 'classes/class_confirm_delete.html', {'class': school_class})
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required

from .models import Department, Subject
from .forms import DepartmentForm

from teachers.models import Teacher
from students.models import Student
from django.http import HttpResponse
import csv


@login_required
def department_list(request):
    qs = Department.objects.all().order_by('name')
    return render(request, 'classes/department_list.html', {'departments': qs})


@login_required
def department_add(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            dept = form.save(commit=False)
            dept.created_by = request.user
            dept.save()
            form.save_m2m()
            messages.success(request, 'Department created')
            return redirect(reverse('classes:department_list'))
    else:
        form = DepartmentForm()
    return render(request, 'classes/department_form.html', {'form': form, 'action': 'Add'})


@login_required
def department_edit(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=dept)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated')
            return redirect(reverse('classes:department_list'))
    else:
        form = DepartmentForm(instance=dept)
    return render(request, 'classes/department_form.html', {'form': form, 'action': 'Edit'})


@login_required
def department_delete(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        dept.delete()
        messages.success(request, 'Department deleted')
        return redirect(reverse('classes:department_list'))
    return render(request, 'classes/department_confirm_delete.html', {'department': dept})


@login_required
def department_detail(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    # dynamic counts
    staff_count = Teacher.objects.filter(department=dept).count()
    # students via subjects or direct link: count students enrolled in subjects of this department
    subjects = dept.subjects.all()
    student_count = Student.objects.filter(subjects__in=subjects).distinct().count()
    courses = subjects
    context = {
        'department': dept,
        'staff_count': staff_count,
        'student_count': student_count,
        'courses': courses,
    }
    return render(request, 'classes/department_detail.html', context)


@login_required
def department_reports(request, pk):
    """Show department reports and allow CSV export."""
    dept = get_object_or_404(Department, pk=pk)
    staff_qs = Teacher.objects.filter(department=dept)
    staff_count = staff_qs.count()
    subjects = dept.subjects.all()
    student_qs = Student.objects.filter(subjects__in=subjects).distinct()
    student_count = student_qs.count()

    # Distribution: teachers per subject
    teacher_distribution = (
        staff_qs.values('id', 'full_name')
        .annotate(subjects_count=Count('subjects'))
        .order_by('-subjects_count')
    )

    # Course distribution
    course_distribution = subjects.annotate(student_count=Count('students')).order_by('-student_count')

    if request.GET.get('export') == 'csv':
        filename = f"department_{dept.id}_report.csv"
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        writer = csv.writer(response)
        writer.writerow(['Department', dept.name])
        writer.writerow(['Staff count', staff_count])
        writer.writerow(['Student count', student_count])
        writer.writerow([])
        writer.writerow(['Teacher', 'Subjects Count'])
        for t in teacher_distribution:
            writer.writerow([t.get('full_name'), t.get('subjects_count')])
        writer.writerow([])
        writer.writerow(['Subject Code', 'Subject Name', 'Student Count'])
        for c in course_distribution:
            writer.writerow([c.code, c.name, c.student_count])
        return response

    context = {
        'department': dept,
        'staff_count': staff_count,
        'student_count': student_count,
        'teacher_distribution': teacher_distribution,
        'course_distribution': course_distribution,
    }
    return render(request, 'classes/department_reports.html', context)
from students.models import Student, Attendance, Grade
from teachers.models import Timetable, Teacher
from notifications.models import Notification
from django.db.models import Avg, Count

# Class Teacher Dashboard
from django.contrib.auth.decorators import login_required
@login_required
def dashboard_class_teacher(request, class_id):
    school_class = SchoolClass.objects.get(pk=class_id)
    teacher = getattr(request.user, 'teacher_profile', None)
    students = Student.objects.filter(school_class=school_class)
    total_students = students.count()
    avg_attendance = Attendance.objects.filter(student__in=students, present=True).aggregate(avg=Avg('present'))['avg'] or 0
    pending_marks = Grade.objects.filter(student__in=students, score=None).count()
    upcoming_events = 0  # Placeholder
    announcements = Notification.objects.filter(recipient_class=school_class).order_by('-date')[:5]

    student_data = []
    for student in students:
        attendance_percent = Attendance.objects.filter(student=student, present=True).count() * 100 // Attendance.objects.filter(student=student).count() if Attendance.objects.filter(student=student).count() else 0
        latest_marks = Grade.objects.filter(student=student).order_by('-year', '-term').first()
        student_data.append({
            'user': student.user,
            'photo': student.photo,
            'parent': student.parent,
            'attendance_percent': attendance_percent,
            'latest_marks': latest_marks.score if latest_marks else '-',
            'attendance_alert': attendance_percent < 75,
        })

    attendance_alerts = [f"{s['user'].get_full_name()} has low attendance ({s['attendance_percent']}%)" for s in student_data if s['attendance_alert']]
    academic_risks = [f"{s['user'].get_full_name()} is at risk academically" for s in student_data if s['latest_marks'] != '-' and s['latest_marks'] < 40]
    timetable = Timetable.objects.filter(school_class=school_class)
    performance_chart_data = []
    attendance_chart_data = []

    context = {
        'user': request.user,
        'class_info': str(school_class),
        'total_students': total_students,
        'avg_attendance': avg_attendance,
        'pending_marks': pending_marks,
        'upcoming_events': upcoming_events,
        'announcements': announcements,
        'students': student_data,
        'attendance_alerts': attendance_alerts,
        'academic_risks': academic_risks,
        'timetable': timetable,
        'performance_chart_data': performance_chart_data,
        'attendance_chart_data': attendance_chart_data,
    }
    return render(request, 'classes/dashboard_class_teacher.html', context)
from django.shortcuts import render, get_object_or_404, redirect
from .models import SchoolClass, Section, Subject, Department
from .forms import SchoolClassForm, SectionForm, SubjectForm, DepartmentForm, DepartmentSubjectForm, DepartmentSearchForm
from django.contrib.auth.decorators import user_passes_test
def is_admin_or_headteacher(user):
    return user.is_authenticated and user.role in ["admin", "headteacher"]

@user_passes_test(is_admin_or_headteacher)
def department_list(request):
    form = DepartmentSearchForm(request.GET or None)
    departments = Department.objects.all()
    if form.is_valid():
        search = form.cleaned_data.get('search')
        head = form.cleaned_data.get('head')
        if search:
            departments = departments.filter(name__icontains=search)
        if head:
            departments = departments.filter(head=head)
    return render(request, "classes/department_list.html", {"departments": departments, "form": form})

@user_passes_test(is_admin_or_headteacher)
def department_add(request):
    if request.method == "POST":
        form = DepartmentForm(request.POST)
        subject_form = DepartmentSubjectForm(request.POST)
        if form.is_valid() and subject_form.is_valid():
            dept = form.save(commit=False)
            template = form.cleaned_data.get('template')
            template_name = form.cleaned_data.get('template_name')
            parent = form.cleaned_data.get('parent')
            auto_populate = form.cleaned_data.get('auto_populate')
            dept.template_name = template_name
            dept.parent = parent
            dept.save()
            if template and auto_populate:
                template_subjects = {
                    'science': ['Physics', 'Chemistry', 'Biology', 'Computer Science'],
                    'mathematics': ['Algebra', 'Geometry', 'Calculus', 'Statistics'],
                    'languages': ['English', 'French', 'Kiswahili', 'Other Languages'],
                }
                for subj_name in template_subjects.get(template, []):
                    subj, _ = Subject.objects.get_or_create(name=subj_name)
                    dept.subjects.add(subj)
            for subj in subject_form.cleaned_data['subjects']:
                dept.subjects.add(subj)
            dept.save()
            # Notify teachers assigned to department
            if dept.head:
                from notifications.models import Notification
                Notification.objects.create(recipient=dept.head.user, message=f"You have been assigned as Head of {dept.name} department.")
            # Notify headteacher
            from users.models import User
            headteacher = User.objects.filter(role="headteacher").first()
            if headteacher:
                from notifications.models import Notification
                Notification.objects.create(recipient=headteacher, message=f"Department {dept.name} created.")
            return redirect("department_list")
    else:
        form = DepartmentForm()
        subject_form = DepartmentSubjectForm()
    return render(request, "classes/department_form.html", {"form": form, "subject_form": subject_form})

@user_passes_test(is_admin_or_headteacher)
def department_edit(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == "POST":
        form = DepartmentForm(request.POST, instance=dept)
        subject_form = DepartmentSubjectForm(request.POST)
        if form.is_valid() and subject_form.is_valid():
            dept = form.save()
            dept.subjects.set(subject_form.cleaned_data['subjects'])
            dept.save()
            # Notify headteacher
            from users.models import User
            headteacher = User.objects.filter(role="headteacher").first()
            if headteacher:
                from notifications.models import Notification
                Notification.objects.create(recipient=headteacher, message=f"Department {dept.name} updated.")
            return redirect("department_list")
    else:
        form = DepartmentForm(instance=dept)
        subject_form = DepartmentSubjectForm(initial={'subjects': dept.subjects.all()})
    return render(request, "classes/department_form.html", {"form": form, "subject_form": subject_form, "edit": True})

@user_passes_test(is_admin_or_headteacher)
def department_delete(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if dept.subjects.exists():
        warning = "Department has assigned subjects. Remove subjects before deleting."
        return render(request, "classes/department_confirm_delete.html", {"department": dept, "warning": warning})
    if request.method == "POST":
        dept.delete()
        return redirect("department_list")
    return render(request, "classes/department_confirm_delete.html", {"department": dept})
from django.contrib.auth.decorators import login_required

@login_required
def class_list(request):
    classes = SchoolClass.objects.select_related('section').all()
    return render(request, "classes/list.html", {"classes": classes})

@login_required
def class_detail(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk)
    return render(request, "classes/detail.html", {"school_class": school_class})

@login_required
def class_create(request):
    if request.method == "POST":
        form = SchoolClassForm(request.POST)
        if form.is_valid():
            school_class = form.save()
            return redirect("classes:detail", pk=school_class.pk)
    else:
        form = SchoolClassForm()
    return render(request, "classes/form.html", {"form": form})

@login_required
def class_edit(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk)
    if request.method == "POST":
        form = SchoolClassForm(request.POST, instance=school_class)
        if form.is_valid():
            form.save()
            return redirect("classes:detail", pk=school_class.pk)
    else:
        form = SchoolClassForm(instance=school_class)
    return render(request, "classes/form.html", {"form": form})

@login_required
def class_delete(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk)
    school_class.delete()
    return redirect("classes:list")

@login_required
def subject_list(request):
    subjects = Subject.objects.select_related('teacher').all()
    return render(request, 'classes/subject_list.html', {'subjects': subjects})


@login_required
def class_students(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk)
    students = Student.objects.filter(school_class=school_class)
    return render(request, 'classes/students_list.html', {'school_class': school_class, 'students': students})


@login_required
def class_assign_students(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk)
    if request.method == 'POST':
        form = AssignStudentsForm(request.POST, school_class=school_class)
        if form.is_valid():
            students = form.cleaned_data['students']
            for s in students:
                s.school_class = school_class
                s.save()
            messages.success(request, 'Students assigned to class')
            return redirect('classes:students', pk=school_class.pk)
    else:
        form = AssignStudentsForm(school_class=school_class)
    return render(request, 'classes/assign_students.html', {'form': form, 'school_class': school_class})


@login_required
def class_promote_students(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk)
    if request.method == 'POST':
        form = PromoteStudentsForm(request.POST, school_class=school_class)
        if form.is_valid():
            students = form.cleaned_data['students']
            target = form.cleaned_data['target_class']
            for s in students:
                s.school_class = target
                s.promoted = True
                s.save()
            messages.success(request, f'{students.count()} students promoted to {target.name}')
            return redirect('classes:detail', pk=target.pk)
    else:
        form = PromoteStudentsForm(school_class=school_class)
    return render(request, 'classes/promote_form.html', {'form': form, 'school_class': school_class})


@login_required
def class_export_csv(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk)
    students = Student.objects.filter(school_class=school_class)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="class_{school_class.name}_students.csv"'
    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Full name', 'Email', 'Parent'])
    for s in students:
        writer.writerow([s.pk, s.user.get_full_name(), getattr(s.user, 'email', ''), getattr(s.parent, 'get_full_name', lambda: '')() if s.parent else ''])
    return response
