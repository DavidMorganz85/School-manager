
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError

# Subject model (missing, needed for imports)
class Subject(models.Model):
	name = models.CharField(max_length=100)
	code = models.CharField(max_length=20, unique=True)

	def __str__(self):
		return f"{self.code} - {self.name}"

class Level(models.Model):
	LEVEL_CHOICES = [
		("O", "O Level"),
		("A", "A Level"),
	]
	name = models.CharField(max_length=2, choices=LEVEL_CHOICES, unique=True)
	description = models.TextField(blank=True)
	def __str__(self):
		return dict(self.LEVEL_CHOICES).get(self.name, self.name)

class Stream(models.Model):
	name = models.CharField(max_length=20)
	school_class = models.ForeignKey('SchoolClass', on_delete=models.CASCADE, related_name='streams')
	class_teacher = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='class_streams')
	def __str__(self):
		return f"{self.school_class} - {self.name}"

class Section(models.Model):
	name = models.CharField(max_length=10)

	def __str__(self):
		return self.name

class Department(models.Model):
	name = models.CharField(max_length=100)
	code = models.CharField(max_length=20, blank=True)
	head = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_departments')
	description = models.TextField(blank=True)
	template = models.CharField(max_length=50, blank=True)
	template_name = models.CharField(max_length=100, blank=True)
	parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_departments')
	subjects = models.ManyToManyField('Subject', blank=True, related_name='departments')
	approved = models.BooleanField(default=False)
	created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_departments')
	approved_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_departments')
	approved_date = models.DateField(null=True, blank=True)

	def __str__(self):
		return self.name

class SchoolClass(models.Model):
	# Basic Information
	name = models.CharField(max_length=20, help_text="e.g., S.1, S.2, S.3, etc.")
	level = models.ForeignKey('Level', on_delete=models.CASCADE, related_name='classes')
    
	# Class Configuration
	SECTION_CHOICES = [
		('A', 'Section A'),
		('B', 'Section B'),
		('C', 'Section C'),
		('D', 'Section D'),
	]
    
	TRACK_CHOICES = [
		('ARTS', 'Arts'),
		('SCIENCE', 'Science'),
		('COMMERCIAL', 'Commercial'),
		('GENERAL', 'General'),
		('TECHNICAL', 'Technical'),
	]
    
	section = models.CharField(max_length=1, choices=SECTION_CHOICES, default='A')
	track = models.CharField(max_length=20, choices=TRACK_CHOICES, blank=True, 
						   help_text="Specialization track for A-Level classes")
    
	# Class Management
	class_teacher = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, 
									null=True, blank=True, related_name='class_teacher_of')
	assistant_class_teacher = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, 
											  null=True, blank=True, related_name='assistant_class_teacher_of')
    
	# Capacity & Resources
	capacity = models.PositiveIntegerField(default=40, validators=[MinValueValidator(1), MaxValueValidator(60)])
	current_student_count = models.PositiveIntegerField(default=0, editable=False)
	room_number = models.CharField(max_length=20, blank=True, help_text="Primary classroom")
	floor = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    
	# Academic Configuration
	subjects = models.ManyToManyField('Subject', through='ClassSubject', related_name='classes')
	compulsory_subjects = models.ManyToManyField('Subject', blank=True, related_name='compulsory_for_classes')
	elective_subjects = models.ManyToManyField('Subject', blank=True, related_name='elective_for_classes')
    
	# Class Performance & Metrics
	class_average = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
	performance_rating = models.CharField(max_length=1, choices=[
		('A', 'Excellent'),
		('B', 'Good'),
		('C', 'Average'),
		('D', 'Below Average'),
		('F', 'Poor'),
	], default='C')
    
	# Attendance & Discipline
	attendance_rate = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)],
									  help_text="Overall class attendance percentage")
	discipline_rating = models.CharField(max_length=1, choices=[
		('A', 'Excellent'),
		('B', 'Good'),
		('C', 'Average'),
		('D', 'Needs Improvement'),
		('F', 'Poor'),
	], default='C')
    
	# Academic Calendar
	academic_year = models.CharField(max_length=9, default="2024/2025", 
								   help_text="e.g., 2024/2025")
	term = models.PositiveIntegerField(choices=[(1, 'Term 1'), (2, 'Term 2'), (3, 'Term 3')], default=1)
    
	# Class Schedule
	start_time = models.TimeField(default='08:00', help_text="Class start time")
	end_time = models.TimeField(default='14:00', help_text="Class end time")
	break_time = models.TimeField(default='10:30', help_text="Break time")
    
	# Resources & Facilities
	has_projector = models.BooleanField(default=False)
	has_computers = models.BooleanField(default=False)
	has_laboratory_access = models.BooleanField(default=False)
	has_library_access = models.BooleanField(default=True)
	special_equipment = models.TextField(blank=True, help_text="Special equipment available for this class")
    
	# Class Status & Metadata
	is_active = models.BooleanField(default=True)
	is_full = models.BooleanField(default=False, editable=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, 
								 null=True, blank=True, related_name='created_classes')
    
	# Class Goals & Targets
	academic_target = models.FloatField(default=75.0, validators=[MinValueValidator(0), MaxValueValidator(100)],
									  help_text="Target average score for the class")
	attendance_target = models.FloatField(default=90.0, validators=[MinValueValidator(0), MaxValueValidator(100)],
										help_text="Target attendance rate")
	promotion_rate_target = models.FloatField(default=95.0, validators=[MinValueValidator(0), MaxValueValidator(100)],
										   help_text="Target promotion rate to next class")
    
	class Meta:
		verbose_name = 'Class'
		verbose_name_plural = 'Classes'
		ordering = ['level', 'name', 'section']
		unique_together = ['name', 'level', 'section', 'academic_year', 'term']
		indexes = [
			models.Index(fields=['level', 'name']),
			models.Index(fields=['academic_year', 'term']),
			models.Index(fields=['class_teacher']),
			models.Index(fields=['is_active']),
		]
    
	def __str__(self):
		base_str = f"{self.name}{self.section} ({self.level})"
		if self.track and self.track != 'GENERAL':
			base_str += f" - {self.track}"
		return base_str
    
	def save(self, *args, **kwargs):
		# Auto-update is_full based on capacity
		self.is_full = self.current_student_count >= self.capacity
        
		# Auto-calculate performance rating based on class average
		if self.class_average >= 85:
			self.performance_rating = 'A'
		elif self.class_average >= 75:
			self.performance_rating = 'B'
		elif self.class_average >= 65:
			self.performance_rating = 'C'
		elif self.class_average >= 50:
			self.performance_rating = 'D'
		else:
			self.performance_rating = 'F'
            
		super().save(*args, **kwargs)
    
	@property
	def full_name(self):
		"""Return full class name with all details"""
		return f"{self.name}{self.section} {self.level} {self.academic_year} Term {self.term}"
    
	@property
	def available_seats(self):
		"""Calculate available seats in the class"""
		return max(0, self.capacity - self.current_student_count)
    
	@property
	def occupancy_rate(self):
		"""Calculate class occupancy percentage"""
		if self.capacity == 0:
			return 0
		return (self.current_student_count / self.capacity) * 100
    
	@property
	def is_o_level(self):
		"""Check if this is an O-Level class"""
		return self.level.name == "O"
    
	@property
	def is_a_level(self):
		"""Check if this is an A-Level class"""
		return self.level.name == "A"
    
	@property
	def needs_attention(self):
		"""Check if class needs administrative attention"""
		return (self.attendance_rate < 80 or 
				self.class_average < 50 or 
				self.discipline_rating in ['D', 'F'])
    
	def get_class_schedule(self):
		"""Get the weekly schedule for this class"""
		# TimetableEntry is defined in this module; reference directly to avoid circular imports
		return TimetableEntry.objects.filter(
			school_class=self,
			academic_year=self.academic_year,
			term=self.term
		).order_by('day', 'start_time')
    
	def get_top_students(self, limit=5):
		"""Get top performing students in the class"""
		from students.models import Student
		return Student.objects.filter(
			current_class=self
		).order_by('-overall_average')[:limit]
    
	def update_class_statistics(self):
		"""Update class statistics based on student data.

		This function is defensive: the `assessment` app or `Result` model may not exist
		in all deployments, so import and calculation are attempted but ignored if missing.
		"""
		from students.models import Student
		try:
			from assessment.models import Result
		except Exception:
			Result = None

		students = Student.objects.filter(current_class=self)

		if not students.exists():
			# No students — reset counters and return
			self.current_student_count = 0
			self.attendance_rate = 0
			self.class_average = 0
			self.save()
			return

		# Update student count
		self.current_student_count = students.count()

		# Calculate average attendance (guard zero-division)
		total_attendance = sum(getattr(student, 'attendance_rate', 0) or 0 for student in students)
		self.attendance_rate = (total_attendance / students.count()) if students.count() else 0

		# Calculate class average if Result model available
		if Result is not None:
			recent_results = Result.objects.filter(student__in=students).order_by('-created_at')[:students.count() * 10]
			if recent_results.exists():
				self.class_average = recent_results.aggregate(models.Avg('marks_obtained'))['marks_obtained__avg'] or 0

		self.save()

# Attendance Reports
class AttendanceReport(models.Model):
	student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='attendance_reports')
	school_class = models.ForeignKey('SchoolClass', on_delete=models.CASCADE, null=True, blank=True)
	stream = models.ForeignKey('Stream', on_delete=models.CASCADE, null=True, blank=True)
	date = models.DateField()
	present = models.BooleanField(default=True)
	term = models.CharField(max_length=20, blank=True)

	def __str__(self):
		return f"{self.student} - {self.date} - {self.present}"

# Discipline
class DisciplineIncident(models.Model):
	student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='discipline_incidents')
	incident_date = models.DateField()
	description = models.TextField()
	reported_by = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True)
	repeated_offense = models.BooleanField(default=False)
	alert_sent = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.student} - {self.incident_date}"

# Library & Resources
class LibraryBook(models.Model):
	title = models.CharField(max_length=200)
	author = models.CharField(max_length=100)
	isbn = models.CharField(max_length=20, unique=True)
	department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='library_books')
	available = models.BooleanField(default=True)

	def __str__(self):
		return self.title

class BookIssue(models.Model):
	book = models.ForeignKey(LibraryBook, on_delete=models.CASCADE, related_name='issues')
	student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='book_issues')
	issue_date = models.DateField(auto_now_add=True)
	return_date = models.DateField(null=True, blank=True)
	overdue = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.book} to {self.student}"

class Resource(models.Model):
	name = models.CharField(max_length=100)
	department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='resources')
	quantity = models.PositiveIntegerField(default=1)
	assigned_to = models.ForeignKey('students.Student', on_delete=models.SET_NULL, null=True, blank=True, related_name='resources')

	def __str__(self):
		return self.name

# Extra-Curricular Activities
class Club(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	teacher_in_charge = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='club_in_charge')

	def __str__(self):
		return self.name

class StudentClub(models.Model):
	student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='clubs')
	club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='members')
	achievement = models.CharField(max_length=200, blank=True)
	participation_date = models.DateField(null=True, blank=True)

	def __str__(self):
		return f"{self.student} in {self.club}"


# Timetable entries for classes/streams
class TimetableEntry(models.Model):
	DAYS = [
		('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'), ('Thu', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday')
	]
	school_class = models.ForeignKey('SchoolClass', on_delete=models.CASCADE, related_name='timetable_entries')
	stream = models.ForeignKey('Stream', on_delete=models.SET_NULL, null=True, blank=True, related_name='timetable_entries')
	subject = models.ForeignKey('Subject', on_delete=models.SET_NULL, null=True, blank=True)
	teacher = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='timetable_entries')
	day = models.CharField(max_length=3, choices=DAYS)
	start_time = models.TimeField()
	end_time = models.TimeField()
	period_label = models.CharField(max_length=50, blank=True)
	room = models.CharField(max_length=50, blank=True)

	class Meta:
		unique_together = ('school_class', 'stream', 'day', 'start_time', 'end_time')

	def __str__(self):
		return f"{self.school_class} {self.stream} {self.day} {self.start_time}-{self.end_time} ({self.subject})"

	def clean(self):
		# Ensure end_time is after start_time
		if self.end_time and self.start_time and self.end_time <= self.start_time:
			raise ValidationError({'end_time': 'End time must be after start time.'})

		# Basic conflict detection for the same class/stream/day
		conflicts = TimetableEntry.objects.filter(
			school_class=self.school_class,
			day=self.day,
		)
		# If stream specified, include stream in conflict checks; otherwise check entries without stream
		if self.stream:
			conflicts = conflicts.filter(stream=self.stream)
		else:
			conflicts = conflicts.filter(stream__isnull=True)

		if self.pk:
			conflicts = conflicts.exclude(pk=self.pk)

		for other in conflicts:
			# Overlap check: start < other.end and end > other.start
			if (self.start_time < other.end_time) and (self.end_time > other.start_time):
				raise ValidationError('This timetable entry overlaps with another entry for the same class/stream/day: %s' % other)

	def conflicts(self):
		"""Return queryset of conflicting timetable entries for this entry (excluding self)."""
		qs = TimetableEntry.objects.filter(school_class=self.school_class, day=self.day)
		if self.stream:
			qs = qs.filter(stream=self.stream)
		else:
			qs = qs.filter(stream__isnull=True)
		if self.pk:
			qs = qs.exclude(pk=self.pk)
		# find overlaps
		conflict_ids = [o.pk for o in qs if (self.start_time < o.end_time) and (self.end_time > o.start_time)]
		return TimetableEntry.objects.filter(pk__in=conflict_ids)


# Lectures (scheduled instances, can link to timetable or be ad-hoc)
class Lecture(models.Model):
	title = models.CharField(max_length=200)
	school_class = models.ForeignKey('SchoolClass', on_delete=models.CASCADE, related_name='lectures')
	stream = models.ForeignKey('Stream', on_delete=models.SET_NULL, null=True, blank=True, related_name='lectures')
	subject = models.ForeignKey('Subject', on_delete=models.SET_NULL, null=True, blank=True)
	teacher = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='lectures')
	date = models.DateField()
	start_time = models.TimeField(null=True, blank=True)
	end_time = models.TimeField(null=True, blank=True)
	resources = models.ManyToManyField('Resource', blank=True)
	attendance_marked = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.title} - {self.school_class} - {self.date}"

	def mark_attendance_complete(self):
		"""Mark lecture as attendance completed and set flag."""
		self.attendance_marked = True
		self.save(update_fields=['attendance_marked'])

	@property
	def duration_minutes(self):
		if self.start_time and self.end_time:
			start_dt = timezone.datetime.combine(self.date, self.start_time)
			end_dt = timezone.datetime.combine(self.date, self.end_time)
			return int((end_dt - start_dt).total_seconds() // 60)
		return None


# Class archival & promotions scaffold
class ClassArchive(models.Model):
	school_class = models.ForeignKey('SchoolClass', on_delete=models.CASCADE, related_name='archives')
	academic_year = models.CharField(max_length=20)
	archived_at = models.DateTimeField(auto_now_add=True)
	notes = models.TextField(blank=True)

	def __str__(self):
		return f"{self.school_class} archived for {self.academic_year}"


class ClassSubject(models.Model):
	"""Through model for Class-Subject relationship with additional data"""
	school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
	subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
	teacher = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True)
	periods_per_week = models.PositiveIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(15)])
	is_compulsory = models.BooleanField(default=True)
	order = models.PositiveIntegerField(default=0, help_text="Display order in class timetable")
	room_preference = models.CharField(max_length=20, blank=True, help_text="Preferred room for this subject")

	class Meta:
		unique_together = ['school_class', 'subject']
		ordering = ['order', 'subject__name']

	def __str__(self):
		return f"{self.school_class} - {self.subject}"


class ClassAnnouncement(models.Model):
	"""Announcements specific to a class"""
	school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='announcements')
	title = models.CharField(max_length=200)
	content = models.TextField()
	priority = models.CharField(max_length=10, choices=[
		('LOW', 'Low'),
		('MEDIUM', 'Medium'),
		('HIGH', 'High'),
		('URGENT', 'Urgent'),
	], default='MEDIUM')
	created_by = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)
	expires_at = models.DateTimeField(null=True, blank=True)
	is_active = models.BooleanField(default=True)
    
	class Meta:
		ordering = ['-created_at']
    
	def __str__(self):
		return f"{self.school_class} - {self.title}"


class ClassEvent(models.Model):
	"""Events specific to a class"""
	school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='events')
	title = models.CharField(max_length=200)
	description = models.TextField(blank=True)
	event_date = models.DateField()
	start_time = models.TimeField()
	end_time = models.TimeField()
	venue = models.CharField(max_length=100, blank=True)
	event_type = models.CharField(max_length=20, choices=[
		('ACADEMIC', 'Academic'),
		('SPORTS', 'Sports'),
		('CULTURAL', 'Cultural'),
		('MEETING', 'Meeting'),
		('OTHER', 'Other'),
	])
	organizer = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE)
    
	class Meta:
		ordering = ['event_date', 'start_time']
    
	def __str__(self):
		return f"{self.school_class} - {self.title} on {self.event_date}"


class ClassResource(models.Model):
	"""Resources shared within a class"""
	school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='resources')
	name = models.CharField(max_length=200)
	description = models.TextField(blank=True)
	resource_file = models.FileField(upload_to='class_resources/')
	resource_type = models.CharField(max_length=20, choices=[
		('NOTES', 'Notes'),
		('ASSIGNMENT', 'Assignment'),
		('REFERENCE', 'Reference'),
		('SYLLABUS', 'Syllabus'),
		('OTHER', 'Other'),
	])
	uploaded_by = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE)
	uploaded_at = models.DateTimeField(auto_now_add=True)
	is_visible_to_students = models.BooleanField(default=True)
    
	class Meta:
		ordering = ['-uploaded_at']
    
	def __str__(self):
		return f"{self.school_class} - {self.name}"


# Attendance records for a lecture
class LectureAttendance(models.Model):
	lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='attendances')
	student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='lecture_attendances')
	present = models.BooleanField(default=False)
	marked_by = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True)
	marked_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ['lecture', 'student']

	def __str__(self):
		return f"{self.student} - {self.lecture} - {'Present' if self.present else 'Absent'}"
