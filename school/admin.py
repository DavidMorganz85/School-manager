from django.contrib import admin
from .models import Student, Teacher, Course, SchoolProfile
from .models import Branch, AcademicYear, Term, ActivityLog

@admin.register(SchoolProfile)
class SchoolProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'tagline', 'email', 'phone')
    fieldsets = (
        (None, {
            'fields': ('name', 'logo', 'tagline', 'mission', 'vision', 'phone', 'email', 'address', 'facebook', 'twitter', 'instagram', 'hero_image', 'about_text', 'features')
        }),
    )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "age")
    search_fields = ("first_name", "last_name", "email")


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email")
    search_fields = ("first_name", "last_name")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "teacher")
    search_fields = ("code", "title")


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'active')


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'active')


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('academic_year', 'name', 'start_date', 'end_date', 'active')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action')
    readonly_fields = ('timestamp',)
