from rest_framework import viewsets, permissions
from .models import Student, Teacher, Course
from .serializers import StudentSerializer, TeacherSerializer, CourseSerializer
from .models import Subject, SchoolClass, Exam, Mark, Attendance, Fee, Book, Route, Notification
from .serializers import (
    SubjectSerializer,
    SchoolClassSerializer,
    ExamSerializer,
    MarkSerializer,
    AttendanceSerializer,
    FeeSerializer,
    BookSerializer,
    RouteSerializer,
    NotificationSerializer,
)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        # allow full access to staff/superusers
        if user.is_staff or user.is_superuser:
            return True
        # allow safe methods to authenticated users
        return request.method in permissions.SAFE_METHODS


class IsTeacherForClassOrReadOnly(permissions.BasePermission):
    """Allow teachers to modify attendance/marks for their classes; students can read their own records."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff or user.is_superuser:
            return True
        # teachers can create/update
        if getattr(user, 'role', None) == 'teacher':
            return True
        # students can read
        if getattr(user, 'role', None) == 'student' and request.method in permissions.SAFE_METHODS:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_staff or user.is_superuser:
            return True
        # students can only view their own records
        if getattr(user, 'role', None) == 'student':
            # attendance/mark object has a `student` FK
            return getattr(obj, 'student', None) and obj.student.user_id == user.id if hasattr(obj.student, 'user_id') else False
        # teachers: allow for now (further restriction by class/subject can be added)
        if getattr(user, 'role', None) == 'teacher':
            return True
        return False


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAdminOrReadOnly]


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAdminOrReadOnly]


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAdminOrReadOnly]


class SchoolClassViewSet(viewsets.ModelViewSet):
    queryset = SchoolClass.objects.all()
    serializer_class = SchoolClassSerializer
    permission_classes = [IsAdminOrReadOnly]


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAdminOrReadOnly]


class MarkViewSet(viewsets.ModelViewSet):
    queryset = Mark.objects.all()
    serializer_class = MarkSerializer
    permission_classes = [IsTeacherForClassOrReadOnly]


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsTeacherForClassOrReadOnly]


class FeeViewSet(viewsets.ModelViewSet):
    queryset = Fee.objects.all()
    serializer_class = FeeSerializer
    permission_classes = [IsAdminOrReadOnly]


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [IsAdminOrReadOnly]


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAdminOrReadOnly]
