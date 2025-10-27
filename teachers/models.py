
from django.db import models
from users.models import User
from classes.models import SchoolClass, Stream, Level, Subject, Department


class Teacher(models.Model):
	# Personal Details
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
	full_name = models.CharField(max_length=100)
	staff_id = models.CharField(max_length=30, unique=True)
	gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
	date_of_birth = models.DateField(null=True, blank=True)
	nationality = models.CharField(max_length=50, blank=True)
	phone = models.CharField(max_length=20, blank=True)
	email = models.EmailField(blank=True)
	address = models.CharField(max_length=255, blank=True)
	photo = models.ImageField(upload_to='teachers/photos/', null=True, blank=True)
	emergency_contact = models.CharField(max_length=100, blank=True)

	# Employment Details
	date_of_joining = models.DateField(null=True, blank=True)
	ROLE_CHOICES = [
		('Teacher', 'Teacher'),
		('Class Teacher', 'Class Teacher'),
		('Subject Teacher', 'Subject Teacher'),
		('HOD', 'Head of Department'),
	]
	role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Teacher')
	EMPLOYMENT_TYPE_CHOICES = [
		('Full-time', 'Full-time'),
		('Part-time', 'Part-time'),
		('Contractual', 'Contractual'),
	]
	employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='Full-time')
	STATUS_CHOICES = [
		('Active', 'Active'),
		('On Leave', 'On Leave'),
		('Retired', 'Retired'),
	]
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
	department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='teachers')
	qualifications = models.TextField(blank=True)
	specializations = models.CharField(max_length=100, blank=True)

	# Academic Responsibilities
	subjects = models.ManyToManyField(Subject, blank=True, related_name='assigned_teachers')
	classes = models.ManyToManyField(SchoolClass, blank=True, related_name='assigned_teachers')
	streams = models.ManyToManyField(Stream, blank=True, related_name='assigned_teachers')
	lesson_plans = models.TextField(blank=True)  # Link to LessonPlan model if available
	teaching_resources = models.TextField(blank=True)  # Link to resources if available
	assessments_notes = models.TextField(blank=True)  # Renamed to avoid clash with Assessment model
	assessments = models.ManyToManyField('Assessment', blank=True, related_name='teachers')
	grades = models.TextField(blank=True)  # Link to Grade model if available
	attendance_record = models.TextField(blank=True)

	# Administrative Responsibilities
	is_hod = models.BooleanField(default=False)
	is_class_teacher = models.BooleanField(default=False)
	committees = models.CharField(max_length=200, blank=True)

	# Extra-Curricular Responsibilities
	clubs_notes = models.CharField(max_length=200, blank=True)  # Renamed to avoid clash with Club model
	clubs = models.ManyToManyField('classes.Club', blank=True, related_name='teachers')
	event_organization = models.TextField(blank=True)
	student_mentoring = models.TextField(blank=True)
	community_service = models.TextField(blank=True)

	# Digital & System Access
	portal_access = models.BooleanField(default=True)
	notifications = models.TextField(blank=True)
	parent_communication = models.TextField(blank=True)
	analytics_access = models.BooleanField(default=True)

	# Performance Tracking
	performance_records = models.TextField(blank=True)
	exam_pass_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
	class_average_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
	feedback = models.TextField(blank=True)
	professional_development = models.TextField(blank=True)
	recognition_awards = models.TextField(blank=True)

	# Relationships

	# Optional Advanced Features
	syllabus_coverage_analytics = models.TextField(blank=True)
	examination_oversight = models.TextField(blank=True)
	multi_role_support = models.BooleanField(default=False)
	digital_archive = models.TextField(blank=True)

	# Availability
	AVAILABILITY_CHOICES = [
		('Available', 'Available'),
		('On Leave', 'On Leave'),
		('Busy', 'Busy'),
		('Unavailable', 'Unavailable'),
	]
	availability_status = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='Available')

	def __str__(self):
		return f"{self.full_name} ({self.staff_id})"

class Timetable(models.Model):
	teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='timetables')
	subject = models.ForeignKey('classes.Subject', on_delete=models.CASCADE)
	school_class = models.ForeignKey('classes.SchoolClass', on_delete=models.CASCADE)
	stream = models.ForeignKey('classes.Stream', on_delete=models.CASCADE, null=True, blank=True, related_name='timetables')
	day = models.CharField(max_length=10)
	period = models.CharField(max_length=10)

	class Meta:
		unique_together = ('teacher', 'day', 'period', 'stream')  # Conflict detection

	def __str__(self):
		return f"{self.teacher} - {self.subject} - {self.school_class} - {self.stream} - {self.day} {self.period}"

	@staticmethod
	def has_conflict(teacher, day, period, stream=None, school_class=None):
		# Check for teacher conflict
		teacher_conflict = Timetable.objects.filter(teacher=teacher, day=day, period=period)
		if stream:
			teacher_conflict = teacher_conflict.filter(stream=stream)
		if teacher_conflict.exists():
			return True
		# Check for classroom conflict
		if school_class:
			class_conflict = Timetable.objects.filter(school_class=school_class, day=day, period=period)
			if class_conflict.exists():
				return True
		return False


# Teacher attendance logging
class TeacherAttendance(models.Model):
	STATUS_CHOICES = [
		('Present', 'Present'),
		('Absent', 'Absent'),
		('On Leave', 'On Leave'),
		('Late', 'Late'),
	]
	teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='attendances')
	date = models.DateField()
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Present')
	note = models.CharField(max_length=255, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('teacher', 'date')

	def __str__(self):
		return f"{self.teacher} - {self.date} - {self.status}"


# Leave requests for teachers
class LeaveRequest(models.Model):
	STATUS = [
		('Pending', 'Pending'),
		('Approved', 'Approved'),
		('Rejected', 'Rejected'),
	]
	teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='leave_requests')
	start_date = models.DateField()
	end_date = models.DateField()
	reason = models.TextField()
	status = models.CharField(max_length=20, choices=STATUS, default='Pending')
	approved_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
	approved_at = models.DateTimeField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Leave: {self.teacher} {self.start_date} → {self.end_date} ({self.status})"


# Substitute assignment when a teacher is absent
class SubstituteAssignment(models.Model):
	original_teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='substitute_from')
	substitute_teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='substitute_for')
	school_class = models.ForeignKey('classes.SchoolClass', on_delete=models.CASCADE)
	subject = models.ForeignKey('classes.Subject', on_delete=models.SET_NULL, null=True, blank=True)
	date = models.DateField()
	period = models.CharField(max_length=20, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('original_teacher', 'date', 'period')

	def __str__(self):
		return f"Substitute on {self.date}: {self.substitute_teacher} for {self.original_teacher}"


# Lesson plan and materials uploaded by teachers
class LessonPlan(models.Model):
	teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='lesson_plans_files')
	title = models.CharField(max_length=200)
	file = models.FileField(upload_to='lesson_plans/', null=True, blank=True)
	subject = models.ForeignKey('classes.Subject', on_delete=models.SET_NULL, null=True, blank=True)
	school_class = models.ForeignKey('classes.SchoolClass', on_delete=models.SET_NULL, null=True, blank=True)
	uploaded_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.title} ({self.teacher})"


# Certificate/Document management for teachers
class TeacherDocument(models.Model):
	teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='documents')
	title = models.CharField(max_length=200)
	file = models.FileField(upload_to='teacher_documents/')
	doc_type = models.CharField(max_length=100, blank=True)
	expiry_date = models.DateField(null=True, blank=True)
	uploaded_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.title} ({self.teacher})"

# Exams & Assessments
class Exam(models.Model):
	EXAM_TYPE_CHOICES = [
		('CAT', 'Continuous Assessment Test'),
		('END_TERM', 'End of Term Exam'),
		('PRACTICAL', 'Practical Exam'),
	]
	name = models.CharField(max_length=100)
	exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES)
	stream = models.ForeignKey('classes.Stream', on_delete=models.CASCADE, related_name='exams')
	subject = models.ForeignKey('classes.Subject', on_delete=models.CASCADE, related_name='exams')
	date = models.DateField()

	def __str__(self):
		return f"{self.name} - {self.exam_type} - {self.stream} - {self.subject}"


# Subject Grouping and Deputy Academic Assignment
class SubjectGroup(models.Model):
	name = models.CharField(max_length=100)
	subjects = models.ManyToManyField(Subject, related_name='groups')
	assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='subject_groups_assigned')  # Deputy Academic
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name

# Basic Assessment model to resolve import error
class Assessment(models.Model):
	teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='assessment_records')
	subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assessments')
	title = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	date = models.DateField(null=True, blank=True)
	max_score = models.PositiveIntegerField(default=100)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.title} ({self.subject}) - {self.teacher}" 
