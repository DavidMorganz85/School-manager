from django.contrib import admin
from .models import Teacher

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'staff_id', 'role', 'department', 'status', 'employment_type')
    search_fields = ('full_name', 'staff_id', 'email', 'phone')
    list_filter = ('role', 'department', 'status', 'employment_type')
    fieldsets = (
        ('Personal Details', {
            'fields': ('user', 'full_name', 'staff_id', 'gender', 'date_of_birth', 'nationality', 'phone', 'email', 'address', 'photo', 'emergency_contact')
        }),
        ('Employment Details', {
            'fields': ('date_of_joining', 'role', 'employment_type', 'status', 'department', 'qualifications', 'specializations')
        }),
        ('Academic Responsibilities', {
            'fields': ('subjects', 'classes', 'streams', 'lesson_plans', 'teaching_resources', 'assessments', 'grades', 'attendance_record')
        }),
        ('Administrative Responsibilities', {
            'fields': ('is_hod', 'is_class_teacher', 'committees')
        }),
        ('Extra-Curricular Responsibilities', {
            'fields': ('clubs', 'event_organization', 'student_mentoring', 'community_service')
        }),
        ('Digital & System Access', {
            'fields': ('portal_access', 'notifications', 'parent_communication', 'analytics_access')
        }),
        ('Performance Tracking', {
            'fields': ('performance_records', 'exam_pass_rate', 'class_average_score', 'feedback', 'professional_development', 'recognition_awards')
        }),
        ('Relationships', {
            'fields': ('timetable',)
        }),
        ('Optional Advanced Features', {
            'fields': ('syllabus_coverage_analytics', 'examination_oversight', 'multi_role_support', 'digital_archive')
        }),
    )
