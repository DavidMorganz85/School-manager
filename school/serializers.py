from rest_framework import serializers
from .models import (
    Student,
    Teacher,
    Course,
    Subject,
    SchoolClass,
    Exam,
    Mark,
    Attendance,
    Fee,
    Book,
    Route,
    Notification,
)


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "title", "code", "teacher"]


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ["id", "first_name", "last_name", "email"]


class StudentSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = ["id", "first_name", "last_name", "email", "age", "enrollment_date", "courses", "photo"]


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "name", "code"]


class SchoolClassSerializer(serializers.ModelSerializer):
    students = StudentSerializer(many=True, read_only=True)

    class Meta:
        model = SchoolClass
        fields = ["id", "name", "section", "teacher", "students"]


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ["id", "title", "subject", "date", "total_marks"]


class MarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mark
        fields = ["id", "student", "exam", "marks_obtained"]


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ["id", "student", "date", "present"]


class FeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fee
        fields = ["id", "student", "amount", "due_date", "paid"]


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id", "title", "author", "isbn", "copies"]


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ["id", "name", "stops", "vehicle"]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "title", "message", "created", "recipients"]
