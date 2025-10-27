from django import forms
from .models import Student, Teacher, Course, Attendance, Mark
from .models import BookLoan, Fee


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["first_name", "last_name", "email", "age", "courses", "photo"]


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ["first_name", "last_name", "email"]


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "code", "teacher"]


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ["student", "date", "present"]


class MarkForm(forms.ModelForm):
    class Meta:
        model = Mark
        fields = ["student", "exam", "marks_obtained"]


class BookLoanForm(forms.ModelForm):
    class Meta:
        model = BookLoan
        fields = ["book", "student", "due_date"]


class FeePaymentForm(forms.ModelForm):
    class Meta:
        model = Fee
        fields = ["student", "amount", "due_date", "paid"]
