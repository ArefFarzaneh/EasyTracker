# Generated by Django 5.0.6 on 2024-07-20 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("EasyTracker", "0014_alter_transaction_amount"),
    ]

    operations = [
        migrations.AddField(
            model_name="wallet",
            name="balance",
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]