# Generated by Django 5.0.6 on 2024-11-17 19:01

import django_jalali.db.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("EasyTracker", "0016_transaction_jalali_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transaction",
            name="jalali_date",
            field=django_jalali.db.models.jDateField(verbose_name="Jalali Date"),
        ),
    ]