
from django.db import models
from students.models import Student

class Book(models.Model):
	title = models.CharField(max_length=200)
	author = models.CharField(max_length=100)
	category = models.CharField(max_length=100, blank=True)
	isbn = models.CharField(max_length=20, blank=True)
	available = models.BooleanField(default=True)

	def __str__(self):
		return self.title

class BorrowRecord(models.Model):
	book = models.ForeignKey(Book, on_delete=models.CASCADE)
	student = models.ForeignKey(Student, on_delete=models.CASCADE)
	borrowed_date = models.DateField(auto_now_add=True)
	due_date = models.DateField()
	returned = models.BooleanField(default=False)
	fine = models.DecimalField(max_digits=6, decimal_places=2, default=0)

	def __str__(self):
		return f"{self.book} borrowed by {self.student}"
