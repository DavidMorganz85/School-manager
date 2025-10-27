
from django.db import models
from students.models import Student
from classes.models import Subject, SchoolClass

class Exam(models.Model):
	name = models.CharField(max_length=100)
	school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
	subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
	date = models.DateField()

	def __str__(self):
		return f"{self.name} - {self.subject} ({self.date})"

class Mark(models.Model):
	exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
	student = models.ForeignKey(Student, on_delete=models.CASCADE)
	score = models.DecimalField(max_digits=5, decimal_places=2)

	def __str__(self):
		return f"{self.student} - {self.exam}: {self.score}"


class ExamType(models.Model):
	name = models.CharField(max_length=100)
	weight = models.FloatField(default=0.0)
	description = models.TextField(blank=True)

	def __str__(self):
		return self.name


class Assessment(models.Model):
	exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE)
	subject = models.ForeignKey('classes.Subject', on_delete=models.CASCADE)
	class_obj = models.ForeignKey('classes.SchoolClass', on_delete=models.CASCADE)
	teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE)
	title = models.CharField(max_length=200)
	total_marks = models.FloatField()
	date_given = models.DateField()
	date_due = models.DateField(null=True, blank=True)

	def __str__(self):
		return f"{self.title} - {self.class_obj}"


class Result(models.Model):
	student = models.ForeignKey(Student, on_delete=models.CASCADE)
	assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
	marks_obtained = models.FloatField()
	grade = models.CharField(max_length=5, blank=True)
	remarks = models.TextField(blank=True)
	created_by = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)

	def save(self, *args, **kwargs):
		try:
			percentage = (self.marks_obtained / self.assessment.total_marks) * 100
		except Exception:
			percentage = 0
		if percentage >= 80:
			self.grade = 'A'
		elif percentage >= 75:
			self.grade = 'B+'
		elif percentage >= 70:
			self.grade = 'B'
		elif percentage >= 65:
			self.grade = 'C+'
		elif percentage >= 60:
			self.grade = 'C'
		elif percentage >= 55:
			self.grade = 'D+'
		elif percentage >= 50:
			self.grade = 'D'
		else:
			self.grade = 'F'
		super().save(*args, **kwargs)

	def __str__(self):
		return f"{self.student} - {self.assessment}"


class GradeScale(models.Model):
	level = models.ForeignKey('classes.Level', on_delete=models.CASCADE)
	grade = models.CharField(max_length=5)
	min_mark = models.FloatField()
	max_mark = models.FloatField()
	points = models.FloatField()
	remark = models.CharField(max_length=50)

	def __str__(self):
		return f"{self.level} - {self.grade}"
