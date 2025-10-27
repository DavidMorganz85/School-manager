from django import forms
from .models import FeeStructure, FeePayment, Invoice

class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['school_class', 'amount', 'description']

class FeePaymentForm(forms.ModelForm):
    class Meta:
        model = FeePayment
        fields = ['student', 'amount', 'invoice']

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        # Invoice model uses `total_amount` and `balance` fields
        fields = ['student', 'total_amount', 'balance']
