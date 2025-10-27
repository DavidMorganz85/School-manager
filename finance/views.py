from django.shortcuts import render, get_object_or_404, redirect
from .models import FeeStructure, FeePayment, Invoice
from .forms import FeeStructureForm, FeePaymentForm, InvoiceForm
from django.contrib.auth.decorators import login_required

@login_required
def finance_dashboard(request):
    structures = FeeStructure.objects.all()
    payments = FeePayment.objects.all()
    invoices = Invoice.objects.all()
    return render(request, "finance/dashboard.html", {"structures": structures, "payments": payments, "invoices": invoices})

@login_required
def fee_payment(request):
    if request.method == "POST":
        form = FeePaymentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("finance:dashboard")
    else:
        form = FeePaymentForm()
    return render(request, "finance/payment_form.html", {"form": form})

@login_required
def invoice_list(request):
    invoices = Invoice.objects.all()
    return render(request, "finance/invoice_list.html", {"invoices": invoices})
