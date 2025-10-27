Migration notes

During development this project had an AUTH_USER_MODEL change and scaffolded apps added.

At one point the migration graph became inconsistent (a migration record for `admin.0001_initial` depended on `users.0001_initial`, but the `users` migration was not recorded as applied). To recover, a developer ran a small sqlite3 script to insert a row into the `django_migrations` table marking `users.0001_initial` as applied.

If you run into InconsistentMigrationHistory errors, prefer these safer steps:

1. Inspect migration files for dependencies. If safe and you have no production data, you can run:

   py manage.py migrate --fake app_label migration_name

2. To mark a migration as applied manually (only for local development), use the Django ORM or sqlite3 to insert into `django_migrations` as was done during earlier debugging.

3. When in doubt, back up `db.sqlite3` before manipulating migration records.
