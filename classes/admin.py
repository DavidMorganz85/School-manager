from django.contrib import admin
from .models import (
    SchoolClass,
    ClassSubject,
    ClassAnnouncement,
    ClassEvent,
    ClassResource,
    ClassArchive,
    Stream,
    Level,
    TimetableEntry,
    Lecture,
    Department,
    Subject,
    Resource,
)


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'section', 'class_teacher', 'current_student_count', 'is_active')
    list_filter = ('level', 'section', 'academic_year', 'term', 'is_active')
    search_fields = ('name', 'room_number')


@admin.register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):
    list_display = ('school_class', 'subject', 'teacher', 'periods_per_week')
    list_filter = ('is_compulsory',)


@admin.register(ClassAnnouncement)
class ClassAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('school_class', 'title', 'priority', 'created_at', 'is_active')
    list_filter = ('priority', 'is_active')


@admin.register(ClassEvent)
class ClassEventAdmin(admin.ModelAdmin):
    list_display = ('school_class', 'title', 'event_date', 'start_time', 'organizer')
    list_filter = ('event_type',)


@admin.register(ClassResource)
class ClassResourceAdmin(admin.ModelAdmin):
    list_display = ('school_class', 'name', 'resource_type', 'uploaded_at')
    list_filter = ('resource_type',)


@admin.register(ClassArchive)
class ClassArchiveAdmin(admin.ModelAdmin):
    list_display = ('school_class', 'academic_year', 'archived_at')


@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ('name', 'school_class', 'class_teacher')
    search_fields = ('name',)


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'head', 'approved')
    search_fields = ('name', 'code')
    raw_id_fields = ('head',)
    filter_horizontal = ('subjects',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'quantity', 'assigned_to')
    search_fields = ('name',)


@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ('school_class', 'stream', 'day', 'start_time', 'end_time', 'subject', 'teacher')
    list_filter = ('day', 'school_class')


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ('title', 'school_class', 'subject', 'date', 'teacher', 'attendance_marked')
    search_fields = ('title',)
