# your_app/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Category, Wallet

DEFAULT_CATEGORIES = ['Salary','Car', 'Rent', 'Travel', 'Clothes','Personal','Shopping','Bill','Food','Entertainment','Pet']

@receiver(post_save, sender=User)
def create_default_categories(sender, instance, created, **kwargs):
    if created:
        for category_name in DEFAULT_CATEGORIES:
            Category.objects.create(name=category_name, user=instance)
        Wallet.objects.create(name = 'Total', user = instance, initial_balance = 0, exclude_from_total = False)


