"""Minimal initial migration for `classes`.

Creates only `Subject` and `Department` so admin pages can load while
deferring teacher-related FKs to a later migration.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Subject",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("code", models.CharField(max_length=20, unique=True)),
            ],
            options={},
        ),
        migrations.CreateModel(
            name="Department",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("code", models.CharField(blank=True, max_length=20)),
                ("description", models.TextField(blank=True)),
                ("parent", models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='sub_departments', to='classes.department')),
            ],
            options={},
        ),
    ]
