from django.core.management.base import BaseCommand
from django.conf import settings
import os
import shutil


class Command(BaseCommand):
    help = (
        "Set school name and optionally copy a local logo into static/images/atlas_logo.png\n"
        "Usage: python manage.py set_school_brand --name 'ATLAS' --logo C:/path/to/logo.png"
    )

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, help='School name to set')
        parser.add_argument('--logo', type=str, help='Path to local image file to copy into static/images/atlas_logo.png')

    def handle(self, *args, **options):
        name = options.get('name')
        logo_path = options.get('logo')

        # Lazy import to avoid app registry issues during migrations
        try:
            from school.models import SchoolProfile
        except Exception as e:
            self.stderr.write(f"Unable to import SchoolProfile: {e}")
            return

        sp, created = SchoolProfile.objects.get_or_create(pk=1, defaults={'name': name or 'ATLAS'})
        if name:
            sp.name = name

        if logo_path:
            if not os.path.exists(logo_path):
                self.stderr.write(self.style.ERROR(f"Logo path not found: {logo_path}"))
            else:
                dest_dir = os.path.join(settings.BASE_DIR, 'static', 'images')
                os.makedirs(dest_dir, exist_ok=True)
                dest_file = os.path.join(dest_dir, 'atlas_logo.png')
                try:
                    shutil.copyfile(logo_path, dest_file)
                    # Attach to model field if available
                    try:
                        from django.core.files import File
                        with open(dest_file, 'rb') as f:
                            sp.logo.save('atlas_logo.png', File(f), save=False)
                    except Exception:
                        # It's ok if saving to model fails (e.g., during migrations), the static file will still exist
                        pass
                    self.stdout.write(self.style.SUCCESS(f"Copied logo to {dest_file}"))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Failed to copy logo: {e}"))

        sp.save()
        self.stdout.write(self.style.SUCCESS(f"SchoolProfile updated: name={sp.name}, logo={bool(sp.logo)}"))
