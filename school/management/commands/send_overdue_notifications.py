from django.core.management.base import BaseCommand
from django.utils import timezone
from school.models import BookLoan, Notification


class Command(BaseCommand):
    help = 'Create Notification records for overdue book loans'

    def handle(self, *args, **options):
        today = timezone.localdate()
        overdue = BookLoan.objects.filter(due_date__lt=today, returned=False)
        created = 0
        for loan in overdue:
            title = f'Overdue book: {loan.book.title}'
            message = f'Book "{loan.book.title}" loaned to {loan.student} was due on {loan.due_date}.'
            n = Notification.objects.create(title=title, message=message)
            n.recipients.add(loan.student)
            created += 1
        self.stdout.write(self.style.SUCCESS(f'Created {created} notifications for overdue loans.'))
