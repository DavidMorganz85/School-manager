from django import forms
from .models import Teacher, Timetable

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            'user', 'full_name', 'staff_id', 'gender', 'date_of_birth', 'nationality', 'phone', 'email', 'address', 'photo', 'emergency_contact',
            'date_of_joining', 'role', 'employment_type', 'status', 'department', 'qualifications', 'specializations',
            'subjects', 'classes', 'streams', 'lesson_plans', 'teaching_resources', 'grades', 'attendance_record',
            'is_hod', 'is_class_teacher', 'committees', 'event_organization', 'student_mentoring', 'community_service',
            'portal_access', 'notifications', 'parent_communication', 'analytics_access',
            'performance_records', 'exam_pass_rate', 'class_average_score', 'feedback', 'professional_development', 'recognition_awards',
            'syllabus_coverage_analytics', 'examination_oversight', 'multi_role_support', 'digital_archive'
        ]

class TimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ['teacher', 'day', 'period', 'subject', 'school_class', 'stream']


from django import forms as _forms
from students.models import Assignment, Submission


class AssignmentForm(_forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'school_class', 'subject', 'total_marks', 'due_date', 'attachment']

    def clean_attachment(self):
        f = self.cleaned_data.get('attachment')
        if f:
            # Basic validation: limit file size to 10MB and allow common types
            max_mb = 10
            if f.size > max_mb * 1024 * 1024:
                raise _forms.ValidationError(f"File too large (>{max_mb}MB)")
            # Basic MIME/type validation
            allowed_mimes = [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'image/png',
                'image/jpeg',
                'text/plain',
                'application/zip',
            ]
            content_type = getattr(f, 'content_type', None)
            if content_type and content_type not in allowed_mimes:
                raise _forms.ValidationError('Unsupported file type.')
            # extension fallback check
            name = getattr(f, 'name', '')
            ext = name.split('.')[-1].lower() if '.' in name else ''
            allowed_ext = ['pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg', 'txt', 'zip']
            if ext and ext not in allowed_ext:
                raise _forms.ValidationError('Unsupported file extension.')
        return f


class GradeForm(_forms.Form):
    marks_obtained = _forms.FloatField(required=True, min_value=0)
    feedback = _forms.CharField(widget=_forms.Textarea, required=False)


from django import forms as _f
from .models import LeaveRequest, LessonPlan, TeacherAttendance


class LeaveRequestForm(_f.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['start_date', 'end_date', 'reason']


class LessonPlanForm(_f.ModelForm):
    class Meta:
        model = LessonPlan
        fields = ['title', 'file', 'subject', 'school_class']


class TeacherAttendanceForm(_f.ModelForm):
    class Meta:
        model = TeacherAttendance
        fields = ['date', 'status', 'note']
