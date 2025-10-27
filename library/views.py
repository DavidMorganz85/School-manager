from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, BorrowRecord
from .forms import BookForm, BorrowRecordForm
from django.contrib.auth.decorators import login_required

@login_required
def library_dashboard(request):
    books = Book.objects.all()
    borrows = BorrowRecord.objects.select_related('book', 'student').all()
    return render(request, "library/dashboard.html", {"books": books, "borrows": borrows})

@login_required
def book_create(request):
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("library:dashboard")
    else:
        form = BookForm()
    return render(request, "library/book_form.html", {"form": form})

@login_required
def borrow_record(request):
    if request.method == "POST":
        form = BorrowRecordForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("library:dashboard")
    else:
        form = BorrowRecordForm()
    return render(request, "library/borrow_form.html", {"form": form})
