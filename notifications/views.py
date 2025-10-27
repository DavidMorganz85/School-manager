from django.shortcuts import render, get_object_or_404, redirect
from .models import Announcement, Notification
from .forms import AnnouncementForm, NotificationForm
from django.contrib.auth.decorators import login_required

@login_required
def announcement_list(request):
    announcements = Announcement.objects.all().order_by('-created_at')
    return render(request, "notifications/announcement_list.html", {"announcements": announcements})

@login_required
def announcement_create(request):
    if request.method == "POST":
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("notifications:announcement_list")
    else:
        form = AnnouncementForm()
    return render(request, "notifications/announcement_form.html", {"form": form})

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-sent_at')
    return render(request, "notifications/notification_list.html", {"notifications": notifications})
