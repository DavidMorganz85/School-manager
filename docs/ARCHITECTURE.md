
# Architecture & Tech Stack

## Recommended stack for production

- Python 3.11+ / 3.12
- Django 5.x
- PostgreSQL for production
- Gunicorn + Nginx (reverse proxy + static files)
- Docker + docker-compose for reproducible deployment
- Celery + Redis for background tasks (notifications, reports, exports)
- AWS S3 (or compatible) for media storage in production
- DRF for API and SimpleJWT for token-based auth

## Folder structure (recommended)

- school_manager_project/ (project)
  - school/ (core models/views/templates)
  - users/ (custom user model, auth)
  - students/, teachers/, classes/, exams/, finance/, library/, transport/, notifications/ (domain apps)
  - templates/
  - static/
  - docs/

## Roles & Responsibilities

### Roles implemented:
- Admin
- Headteacher/Principal
- Deputy Headteacher
- Director of Studies
- Head of Department
- Teacher
- Student
- Non-Teaching Staff (Accounts, Welfare, Cleaner/Support, IT Support)

### Responsibilities & Features:
- Role-based dashboards for each role
- Role assignment and deactivation (admin/headteacher)
- Student CRUD, attendance, results, fees, notifications, library/resources
- Teacher dashboard: timetable, attendance, marks entry, notifications
- Class teacher dashboard: class/subject management, student overview
- Headteacher dashboard: school-wide metrics, staff management, notifications
- Non-teaching staff dashboards: accounts, welfare, support, IT

### Security & Access Control
- Custom user model with role/sub-role fields
- Role-based access control in views and templates
- Secure login/registration with Redena-style UI/UX
- Password reset, account lockout, session management

### Dashboards
- Responsive dashboards for all roles
- Metrics, charts, notifications, management features
- Student dashboard: subjects, attendance, GPA, fee status, profile, results, report card, finance, class/timetable, notifications, library/resources
- Teacher dashboard: timetable, attendance, marks, notifications
- Class teacher dashboard: class/subject info, student overview
- Headteacher dashboard: school-wide metrics, staff management

## Operational notes

- Use environment variables for secrets and DB config.
- Run production migrations on a maintenance window with backups.
- Add monitoring (Sentry), logging, and health checks.
