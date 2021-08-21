from django.db import models

from crypto_wallet.constants import CURRENCIES


class Wallet(models.Model):
    currency = models.CharField(max_length=3, choices=CURRENCIES.CHOICES)
    address = models.CharField(max_length=42, unique=True)
    private_key = models.CharField(max_length=255)
