from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from users.models import User

class Command(BaseCommand):
    help = 'Setup default user roles/groups and create a superuser if none exists'

    def handle(self, *args, **options):
        roles = ['admin', 'headteacher', 'teacher', 'student', 'parent', 'staff']
        for role in roles:
            group, created = Group.objects.get_or_create(name=role)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created group: {role}'))
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(username='admin', email='admin@example.com', password='admin123', role='admin', is_approved=True)
            self.stdout.write(self.style.SUCCESS('Created superuser: admin (password: admin123)'))
        else:
            self.stdout.write(self.style.NOTICE('Superuser already exists.'))
