
from django.urls import path
from .views import student_dashboard, student_list, assignments_list, assignment_detail, materials_list, inbox, send_message

app_name = "students"

urlpatterns = [
    path('dashboard/', student_dashboard, name='student_dashboard'),
    path('', student_list, name='list'),
    path('assignments/', assignments_list, name='assignments'),
    path('assignments/<int:pk>/', assignment_detail, name='assignment_detail'),
    path('materials/', materials_list, name='materials'),
    path('messages/', inbox, name='inbox'),
    path('messages/send/', send_message, name='send_message'),
    # student endpoints
]
