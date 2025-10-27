from django import forms
from .models import SchoolClass, ClassAnnouncement, ClassEvent, ClassResource


class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ['name', 'level', 'section', 'track', 'class_teacher', 'assistant_class_teacher', 'capacity', 'room_number', 'floor', 'academic_year', 'term', 'start_time', 'end_time', 'break_time', 'has_projector', 'has_computers', 'has_laboratory_access', 'has_library_access']


class ClassAnnouncementForm(forms.ModelForm):
    class Meta:
        model = ClassAnnouncement
        fields = ['school_class', 'title', 'content', 'priority', 'expires_at', 'is_active']


class ClassEventForm(forms.ModelForm):
    class Meta:
        model = ClassEvent
        fields = ['school_class', 'title', 'description', 'event_date', 'start_time', 'end_time', 'venue', 'event_type']


class ClassResourceForm(forms.ModelForm):
    class Meta:
        model = ClassResource
        fields = ['school_class', 'name', 'description', 'resource_file', 'resource_type', 'is_visible_to_students']


class AssignStudentsForm(forms.Form):
    students = forms.ModelMultipleChoiceField(queryset=None, widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        school_class = kwargs.pop('school_class', None)
        super().__init__(*args, **kwargs)
        if school_class:
            from students.models import Student
            # allow students not currently assigned or in other classes
            self.fields['students'].queryset = Student.objects.filter(school_class__isnull=True)
        else:
            self.fields['students'].queryset = Student.objects.none()


class PromoteStudentsForm(forms.Form):
    students = forms.ModelMultipleChoiceField(queryset=None, widget=forms.CheckboxSelectMultiple)
    target_class = forms.ModelChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        school_class = kwargs.pop('school_class', None)
        super().__init__(*args, **kwargs)
        from students.models import Student
        from .models import SchoolClass
        if school_class:
            self.fields['students'].queryset = Student.objects.filter(school_class=school_class)
        else:
            self.fields['students'].queryset = Student.objects.none()
        self.fields['target_class'].queryset = SchoolClass.objects.exclude(pk=getattr(school_class, 'pk', None))

from django import forms
from .models import Department


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code', 'head', 'description', 'subjects', 'parent', 'approved']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'subjects': forms.CheckboxSelectMultiple,
        }

from django import forms
from .models import Subject, SchoolClass, Section, Department
from teachers.models import Teacher
from students.models import Student


class AssignStudentsForm(forms.Form):
    students = forms.ModelMultipleChoiceField(queryset=Student.objects.none(), required=True)

    def __init__(self, *args, **kwargs):
        school_class = kwargs.pop('school_class', None)
        super().__init__(*args, **kwargs)
        if school_class:
            # allow selecting only students not already in this class or all students
            self.fields['students'].queryset = Student.objects.filter(school_class__isnull=True) | Student.objects.filter(school_class=school_class)
        else:
            self.fields['students'].queryset = Student.objects.all()


class PromoteStudentsForm(forms.Form):
    students = forms.ModelMultipleChoiceField(queryset=Student.objects.none(), required=True)
    target_class = forms.ModelChoiceField(queryset=SchoolClass.objects.all(), required=True)

    def __init__(self, *args, **kwargs):
        school_class = kwargs.pop('school_class', None)
        super().__init__(*args, **kwargs)
        if school_class:
            self.fields['students'].queryset = Student.objects.filter(school_class=school_class)
        else:
            self.fields['students'].queryset = Student.objects.all()

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name']

class SectionForm(forms.ModelForm):
    class Meta:
        model = __import__('classes.models', fromlist=['Section']).Section
        fields = ['name']

class DepartmentForm(forms.ModelForm):
    template = forms.ChoiceField(
        choices=[
            ('', 'Select Template'),
            ('science', 'Science'),
            ('mathematics', 'Mathematics'),
            ('languages', 'Languages'),
            ('custom', 'Custom'),
        ], required=False
    )
    auto_populate = forms.BooleanField(required=False, label='Auto-populate subjects from template')
    parent = forms.ModelChoiceField(queryset=Department.objects.all(), required=False, label='Parent Department')
    template_name = forms.CharField(required=False, label='Template Name')
    class Meta:
        model = Department
        fields = ['name', 'code', 'head', 'description', 'template', 'template_name', 'parent']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }

class DepartmentSubjectForm(forms.Form):
    subjects = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(), required=False)


class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = __import__('classes.models', fromlist=['SchoolClass']).SchoolClass
        fields = ['name', 'section']

class DepartmentSearchForm(forms.Form):
    search = forms.CharField(required=False, label='Search Department')
    head = forms.ModelChoiceField(queryset=Teacher.objects.all(), required=False)
