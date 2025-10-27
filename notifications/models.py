
from django.db import models
from django.conf import settings


class Announcement(models.Model):
	title = models.CharField(max_length=200)
	message = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

	def __str__(self):
		return self.title


class Notification(models.Model):
	recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	message = models.TextField()
	sent_at = models.DateTimeField(auto_now_add=True)
	read = models.BooleanField(default=False)
	# optional: notification targeted at a class (for class-level notices)
	recipient_class = models.ForeignKey('classes.SchoolClass', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')

	def __str__(self):
		return f"To {self.recipient}: {self.message[:30]}..."
