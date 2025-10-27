from django.urls import path
from . import views

app_name = 'classes'

urlpatterns = [
    path('', views.class_list, name='class_list'),
    path('create/', views.class_create, name='class_create'),
    path('<int:pk>/', views.class_detail, name='class_detail'),
    path('<int:pk>/edit/', views.class_edit, name='class_edit'),
    path('<int:pk>/delete/', views.class_delete, name='class_delete'),
]
from django.urls import path

from . import views

app_name = "classes"

urlpatterns = [
    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.department_add, name='department_add'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
    path('departments/<int:pk>/', views.department_detail, name='department_detail'),
    path('departments/<int:pk>/reports/', views.department_reports, name='department_reports'),
    # classes endpoints
    path('classes/', views.class_list, name='list'),
    path('classes/add/', views.class_create, name='create'),
    path('classes/<int:pk>/', views.class_detail, name='detail'),
    path('classes/<int:pk>/edit/', views.class_edit, name='edit'),
    path('classes/<int:pk>/delete/', views.class_delete, name='delete'),
    path('classes/<int:pk>/students/', views.class_students, name='students'),
    path('classes/<int:pk>/assign/', views.class_assign_students, name='assign_students'),
    path('classes/<int:pk>/promote/', views.class_promote_students, name='promote_students'),
    path('classes/<int:pk>/export/', views.class_export_csv, name='export_csv'),
]
