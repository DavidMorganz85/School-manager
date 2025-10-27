from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Student, Attendance
from django.test import TestCase


User = get_user_model()


class AttendanceAPITest(APITestCase):
	def setUp(self):
		# create a teacher user
		self.teacher = User.objects.create_user(username='t1', password='pass', role='teacher')
		# create a student and associated user (simplified)
		self.student = Student.objects.create(first_name='S', last_name='One')

	def test_teacher_can_create_attendance(self):
		# Create attendance via ORM as a smoke test for model and DB wiring
		a = Attendance.objects.create(student=self.student, date='2025-10-20', present=True)
		self.assertIsNotNone(a.id)

class BookLoanTest(TestCase):
	def test_bookloan_checkout_and_return(self):
		from .models import Book, Student, BookLoan
		b = Book.objects.create(title='Django for Pros', author='A', copies=2)
		s = Student.objects.create(first_name='Jane', last_name='Doe')
		loan = BookLoan.objects.create(book=b, student=s, due_date='2025-12-01')
		# copies should have decreased
		b.refresh_from_db()
		self.assertEqual(b.copies, 1)
		# return the book
		loan.mark_returned()
		loan.refresh_from_db()
		b.refresh_from_db()
		self.assertTrue(loan.returned)
		self.assertEqual(b.copies, 2)
