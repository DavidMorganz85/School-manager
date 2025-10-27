from django import forms
from .models import Student, Attendance, Grade

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['photo', 'school_class', 'parent', 'date_of_birth', 'address']

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['date', 'subject', 'present']

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['subject', 'score', 'term', 'year']
