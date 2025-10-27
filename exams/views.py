from django.shortcuts import render, get_object_or_404, redirect
from .models import Exam, Mark
from .forms import ExamForm, MarkForm
from django.contrib.auth.decorators import login_required

@login_required
def exam_list(request):
    exams = Exam.objects.select_related('school_class', 'subject').all()
    return render(request, "exams/list.html", {"exams": exams})

@login_required
def exam_detail(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    return render(request, "exams/detail.html", {"exam": exam})

@login_required
def exam_create(request):
    if request.method == "POST":
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save()
            return redirect("exams:detail", pk=exam.pk)
    else:
        form = ExamForm()
    return render(request, "exams/form.html", {"form": form})

@login_required
def mark_list(request):
    marks = Mark.objects.select_related('student', 'exam').all()
    return render(request, 'exams/mark_list.html', {'marks': marks})
