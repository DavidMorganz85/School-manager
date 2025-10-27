
from django.urls import path
from .views import (
    teacher_dashboard, teacher_list,
    teacher_assignments_list, teacher_create_assignment, teacher_submissions_list,
    teacher_grade_submission, teacher_grade_submission_ajax,
    leave_request_create, leave_request_list, leave_request_approve,
    teacher_attendance_log, lessonplan_upload,
)

app_name = "teachers"

urlpatterns = [
    path('dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path('', teacher_list, name='list'),
    # teacher endpoints
    path('assignments/', teacher_assignments_list, name='assignments_list'),
    path('assignments/create/', teacher_create_assignment, name='create_assignment'),
    path('assignments/<int:assignment_id>/submissions/', teacher_submissions_list, name='assignment_submissions'),
    path('assignments/<int:assignment_id>/submissions/<int:submission_id>/grade/', teacher_grade_submission, name='grade_submission'),
    path('assignments/<int:assignment_id>/submissions/<int:submission_id>/grade/ajax/', teacher_grade_submission_ajax, name='grade_submission_ajax'),
    # leave requests
    path('leave/submit/', leave_request_create, name='leave_request_create'),
    path('leave/', leave_request_list, name='leave_requests'),
    path('leave/<int:pk>/action/', leave_request_approve, name='leave_request_action'),
    # attendance
    path('attendance/', teacher_attendance_log, name='attendance_log'),
    # lesson plans
    path('lessonplans/', lessonplan_upload, name='lessonplans'),
]
