
from django.db import models
from classes.models import SchoolClass, Stream, Level, Subject
from users.models import User

class Student(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
	photo = models.ImageField(upload_to='students/photos/', null=True, blank=True)
	school_class = models.ForeignKey(SchoolClass, on_delete=models.SET_NULL, null=True, blank=True)
	stream = models.ForeignKey(Stream, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
	level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
	subjects = models.ManyToManyField(Subject, blank=True, related_name='students')
	parent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
	date_of_birth = models.DateField(null=True, blank=True)
	address = models.CharField(max_length=255, blank=True)
	promoted = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.user.get_full_name()} ({self.school_class} - {self.stream} - {self.level})"

class Attendance(models.Model):
	student = models.ForeignKey(Student, on_delete=models.CASCADE)
	date = models.DateField()
	subject = models.CharField(max_length=100, blank=True)
	present = models.BooleanField(default=True)

	def __str__(self):
		return f"{self.student} - {self.date} - {self.subject}"

class Grade(models.Model):
	student = models.ForeignKey(Student, on_delete=models.CASCADE)
	subject = models.CharField(max_length=100)
	score = models.DecimalField(max_digits=5, decimal_places=2)
	term = models.CharField(max_length=20)
	year = models.IntegerField()

	def __str__(self):
		return f"{self.student} - {self.subject}: {self.score}"


# Promotion workflow
class Promotion(models.Model):
	student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='promotions')
	from_level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True, related_name='promoted_from')
	to_level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True, related_name='promoted_to')
	date = models.DateField(auto_now_add=True)
	promoted_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)

	def __str__(self):
		return f"{self.student} {self.from_level} → {self.to_level}"

# Subject combinations for A-Level electives
class SubjectCombination(models.Model):
	STREAM_CHOICES = [
		('Arts', 'Arts'),
		('Science', 'Science'),
	]
	student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='subject_combinations')
	stream = models.CharField(max_length=10, choices=STREAM_CHOICES)
	subjects = models.ManyToManyField(Subject, related_name='combinations')

	def __str__(self):
		return f"{self.student} - {self.stream}"

# Archive graduated/left students
class StudentArchive(models.Model):
	student = models.OneToOneField('Student', on_delete=models.CASCADE, related_name='archive')
	reason = models.CharField(max_length=100)
	date = models.DateField(auto_now_add=True)

	def __str__(self):
		return f"{self.student} archived: {self.reason}"


# New student-facing features
class Assignment(models.Model):
	title = models.CharField(max_length=200)
	description = models.TextField(blank=True)
	school_class = models.ForeignKey('classes.SchoolClass', on_delete=models.CASCADE, related_name='assignments')
	subject = models.ForeignKey('classes.Subject', on_delete=models.SET_NULL, null=True, blank=True)
	teacher = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True)
	total_marks = models.PositiveIntegerField(default=100)
	due_date = models.DateField(null=True, blank=True)
	attachment = models.FileField(upload_to='assignments/', null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.title} ({self.school_class})"


class Submission(models.Model):
	assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
	student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='submissions')
	file = models.FileField(upload_to='submissions/', null=True, blank=True)
	marks_obtained = models.FloatField(null=True, blank=True)
	feedback = models.TextField(blank=True)
	submitted_at = models.DateTimeField(auto_now_add=True)
	graded_by = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True)

	class Meta:
		unique_together = ('assignment', 'student')

	def __str__(self):
		return f"Submission: {self.assignment.title} by {self.student}"


class Material(models.Model):
	title = models.CharField(max_length=200)
	file = models.FileField(upload_to='materials/', null=True, blank=True)
	school_class = models.ForeignKey('classes.SchoolClass', on_delete=models.SET_NULL, null=True, blank=True, related_name='materials')
	uploaded_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
	uploaded_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.title


class Message(models.Model):
	sender = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='sent_messages')
	recipient = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='received_messages')
	subject = models.CharField(max_length=200, blank=True)
	body = models.TextField()
	sent_at = models.DateTimeField(auto_now_add=True)
	read = models.BooleanField(default=False)

	def __str__(self):
		return f"Message from {self.sender} to {self.recipient} - {self.subject}"
