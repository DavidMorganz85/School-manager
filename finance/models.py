
from django.db import models
from students.models import Student

class FeeStructure(models.Model):
	school_class = models.ForeignKey('classes.SchoolClass', on_delete=models.CASCADE)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	description = models.CharField(max_length=255, blank=True)

	def __str__(self):
		return f"{self.school_class}: {self.amount}"

class FeePayment(models.Model):
	student = models.ForeignKey(Student, on_delete=models.CASCADE)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	date_paid = models.DateField(auto_now_add=True)
	invoice = models.CharField(max_length=50, blank=True)

	def __str__(self):
		return f"{self.student} - {self.amount} on {self.date_paid}"

class Invoice(models.Model):
	student = models.ForeignKey(Student, on_delete=models.CASCADE)
	invoice_number = models.CharField(max_length=20, unique=True, blank=True)
	due_date = models.DateField()
	issue_date = models.DateField(auto_now_add=True)
	status = models.CharField(max_length=20, choices=(
		('pending', 'Pending'),
		('paid', 'Paid'),
		('overdue', 'Overdue'),
		('cancelled', 'Cancelled'),
	), default='pending')
	total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

	def save(self, *args, **kwargs):
		if not self.invoice_number:
			last = Invoice.objects.order_by('-id').first()
			last_num = int(last.invoice_number.split('-')[-1]) if last and last.invoice_number else 0
			self.invoice_number = f"INV-{last_num + 1:06d}"
		super().save(*args, **kwargs)

	def __str__(self):
		return self.invoice_number


class Payment(models.Model):
	invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
	amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
	payment_date = models.DateField()
	payment_method = models.CharField(max_length=20, choices=(
		('cash', 'Cash'),
		('bank', 'Bank Transfer'),
		('mobile_money', 'Mobile Money'),
		('cheque', 'Cheque'),
	))
	receipt_number = models.CharField(max_length=20, unique=True)
	confirmed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)

	def __str__(self):
		return f"Payment {self.receipt_number}"


class Expense(models.Model):
	category = models.CharField(max_length=100)
	description = models.TextField()
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	date_incurred = models.DateField()
	approved_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)

	def __str__(self):
		return f"{self.category} - {self.amount}"
