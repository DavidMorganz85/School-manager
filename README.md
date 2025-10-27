School Manager - Fedena-like MVP

This repository contains a small Django-based school management project scaffold.

Quick start (development):

1. Create and activate a Python virtual environment (Windows cmd.EXE):

   py -3 -m venv .venv
   .venv\Scripts\activate

2. Install dependencies:

   pip install -r requirements.txt

3. Make migrations & migrate:

   py manage.py makemigrations
   py manage.py migrate

4. Create a superuser and run server:

   py manage.py createsuperuser
   py manage.py runserver

Notes:
- If you changed `AUTH_USER_MODEL` after migrations were created, you may need to reconcile migration history. During development, a manual insertion into `django_migrations` was used to mark `users.0001_initial` as applied. See `docs/MIGRATION_NOTES.md` for details.
- MEDIA files are served in DEBUG mode from `/media/`.

Next steps:
- Implement role-based dashboards, JWT registration flow, attendance/exams modules, and production deployment (Postgres + Docker).
