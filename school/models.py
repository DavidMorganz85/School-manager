from django.db import models

class SchoolProfile(models.Model):
	name = models.CharField(max_length=100, default="ATLAS")
	logo = models.ImageField(upload_to='school/logo/', null=True, blank=True)
	tagline = models.CharField(max_length=200, blank=True)
	mission = models.TextField(blank=True)
	vision = models.TextField(blank=True)
	phone = models.CharField(max_length=20, blank=True)
	email = models.EmailField(blank=True)
	address = models.CharField(max_length=255, blank=True)
	facebook = models.URLField(blank=True)
	twitter = models.URLField(blank=True)
	instagram = models.URLField(blank=True)
	hero_image = models.ImageField(upload_to='school/hero/', null=True, blank=True)
	about_text = models.TextField(blank=True)
	features = models.TextField(blank=True)

	def __str__(self):
		return self.name
from django.db import models


class Teacher(models.Model):
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	email = models.EmailField(blank=True)

	class Meta:
		ordering = ["last_name", "first_name"]

	def __str__(self) -> str:
		return f"{self.first_name} {self.last_name}"


class Course(models.Model):
	title = models.CharField(max_length=100)
	code = models.CharField(max_length=20, unique=True)
	teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)

	class Meta:
		ordering = ["code"]

	def __str__(self) -> str:
		return f"{self.code} - {self.title}"


class Student(models.Model):
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	email = models.EmailField(blank=True)
	age = models.PositiveSmallIntegerField(null=True, blank=True)
	enrollment_date = models.DateField(auto_now_add=True)
	courses = models.ManyToManyField(Course, blank=True, related_name="students")
	photo = models.ImageField(upload_to='student_photos/', null=True, blank=True)

	class Meta:
		ordering = ["last_name", "first_name"]

	def __str__(self) -> str:
		return f"{self.first_name} {self.last_name}"


class Subject(models.Model):
	name = models.CharField(max_length=100)
	code = models.CharField(max_length=20, unique=True)

	def __str__(self) -> str:
		return f"{self.code} - {self.name}"


class SchoolClass(models.Model):
	name = models.CharField(max_length=100)
	section = models.CharField(max_length=10, blank=True)
	teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
	students = models.ManyToManyField(Student, blank=True, related_name='classes')

	class Meta:
		verbose_name = "Class"
		verbose_name_plural = "Classes"

	def __str__(self) -> str:
		return f"{self.name}{(' - ' + self.section) if self.section else ''}"


class Exam(models.Model):
	title = models.CharField(max_length=150)
	subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
	date = models.DateField()
	total_marks = models.PositiveIntegerField(default=100)

	def __str__(self) -> str:
		return f"{self.title} - {self.subject.code}"


class Mark(models.Model):
	student = models.ForeignKey(Student, on_delete=models.CASCADE)
	exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
	marks_obtained = models.DecimalField(max_digits=6, decimal_places=2)

	class Meta:
		unique_together = ("student", "exam")

	def __str__(self) -> str:
		return f"{self.student} - {self.exam}: {self.marks_obtained}"


class Attendance(models.Model):
	student = models.ForeignKey(Student, on_delete=models.CASCADE)
	date = models.DateField()
	present = models.BooleanField(default=True)

	class Meta:
		unique_together = ("student", "date")

	def __str__(self) -> str:
		return f"{self.date} - {self.student} - {'Present' if self.present else 'Absent'}"


class Fee(models.Model):
	student = models.ForeignKey(Student, on_delete=models.CASCADE)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	due_date = models.DateField()
	paid = models.BooleanField(default=False)

	def __str__(self) -> str:
		return f"{self.student} - {'Paid' if self.paid else 'Due'} {self.amount}"


class Book(models.Model):
	title = models.CharField(max_length=200)
	author = models.CharField(max_length=200, blank=True)
	isbn = models.CharField(max_length=20, blank=True)
	copies = models.PositiveIntegerField(default=1)

	def __str__(self) -> str:
		return f"{self.title} by {self.author}"


class Route(models.Model):
	name = models.CharField(max_length=100)
	stops = models.TextField(blank=True)
	vehicle = models.CharField(max_length=100, blank=True)

	def __str__(self) -> str:
		return self.name


class Notification(models.Model):
	title = models.CharField(max_length=200)
	message = models.TextField()
	created = models.DateTimeField(auto_now_add=True)
	recipients = models.ManyToManyField(Student, blank=True)

	def __str__(self) -> str:
		return f"{self.title} - {self.created.strftime('%Y-%m-%d %H:%M')}"


class BookLoan(models.Model):
	book = models.ForeignKey(Book, on_delete=models.CASCADE)
	student = models.ForeignKey(Student, on_delete=models.CASCADE)
	checkout_date = models.DateField(auto_now_add=True)
	due_date = models.DateField()
	returned = models.BooleanField(default=False)

	def save(self, *args, **kwargs):
		# decrement copies on checkout
		if not self.pk:
			if self.book.copies > 0:
				self.book.copies -= 1
				self.book.save()
		super().save(*args, **kwargs)

	def mark_returned(self):
		if not self.returned:
			self.returned = True
			self.book.copies += 1
			self.book.save()
			self.save()

	def __str__(self) -> str:
		return f"{self.book.title} loan to {self.student}"


# School administration models
class Branch(models.Model):
	name = models.CharField(max_length=100)
	address = models.CharField(max_length=255, blank=True)
	phone = models.CharField(max_length=20, blank=True)
	email = models.EmailField(blank=True)
	active = models.BooleanField(default=True)

	def __str__(self):
		return self.name


class AcademicYear(models.Model):
	name = models.CharField(max_length=50)  # e.g., 2025/2026
	start_date = models.DateField()
	end_date = models.DateField()
	active = models.BooleanField(default=False)

	def __str__(self):
		return self.name


class Term(models.Model):
	academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='terms')
	name = models.CharField(max_length=50)  # e.g., Term 1
	start_date = models.DateField()
	end_date = models.DateField()
	active = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.academic_year.name} - {self.name}"


class ActivityLog(models.Model):
	user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
	action = models.CharField(max_length=200)
	timestamp = models.DateTimeField(auto_now_add=True)
	metadata = models.JSONField(blank=True, null=True)

	def __str__(self):
		return f"{self.timestamp} - {self.user}: {self.action}"
