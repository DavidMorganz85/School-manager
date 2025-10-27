from django.urls import path
from . import views

app_name = "school"

urlpatterns = [
    path("", views.landing, name="index"),
    path("students/new/", views.student_create, name="student_create"),
    path("students/<int:pk>/", views.student_detail, name="student_detail"),
    path("teachers/", views.teacher_list, name="teacher_list"),
    path("teachers/new/", views.teacher_create, name="teacher_create"),
    path("teachers/<int:pk>/", views.teacher_detail, name="teacher_detail"),
    path("courses/", views.course_list, name="course_list"),
    path("courses/new/", views.course_create, name="course_create"),
    path("courses/<int:pk>/", views.course_detail, name="course_detail"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("summary/", views.admin_summary, name="admin_summary"),
    path("summary/data/", views.summary_chart_data, name="summary_chart_data"),
    path("attendance/", views.attendance_list, name="attendance_list"),
    path("attendance/new/", views.attendance_create, name="attendance_create"),
    path("marks/", views.marks_list, name="marks_list"),
    path("marks/new/", views.mark_create, name="mark_create"),
    path("bookloans/", views.bookloans_list, name="bookloan_list"),
    path("bookloans/new/", views.bookloan_create, name="bookloan_create"),
    path("bookloans/<int:pk>/return/", views.bookloan_return, name="bookloan_return"),
    path("fees/", views.fees_list, name="fees_list"),
    path("fees/<int:pk>/toggle/", views.fee_toggle_paid, name="fee_toggle_paid"),
]


