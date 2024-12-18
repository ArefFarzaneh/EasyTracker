# Generated by Django 5.0.6 on 2024-06-11 16:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("EasyTracker", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="user",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="transactions",
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
    ]
