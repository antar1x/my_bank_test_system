from django.core.validators import MinValueValidator, MinLengthValidator
from django.db import models
from django.contrib.auth.models import User
from bank.errors import NotEnoughBalance
from bank.functions import generate_card_number, generate_cvv, default_expiry_date


class Account(models.Model):
    CURRENCY_CHOICES = (
        ('USD', 'USD'),
        ('UAH', 'UAH'),
        ('EUR', 'EUR'),
    )
    ownerName = models.CharField(max_length=100)
    balance = models.DecimalField(decimal_places=2, max_digits=10, default=0, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    date_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.ownerName} - {self.balance} {self.currency}"

class Transaction(models.Model):
    TRANSACTION_CHOICES = (
        ("WITHDRAW", "WITHDRAW"),
        ("DEPOSIT", "DEPOSIT"),
    )

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        validators=[MinValueValidator(0.01)],
    )
    date_created = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_CHOICES,
        default="DEPOSIT",
    )
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.transaction_type == "DEPOSIT":
                self.account.balance += self.amount
            elif self.transaction_type == "WITHDRAW":
                if self.account.balance < self.amount:
                    raise NotEnoughBalance("Not enough money")
                self.account.balance -= self.amount

            self.account.save()

        super().save(*args, **kwargs)


class Transfer(models.Model):
    from_account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="outgoing_transfers"
    )

    to_account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="incoming_transfers"
    )

    amount = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        validators=[MinValueValidator(0.01)],
    )

    description = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

class Card(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="cards")
    card_number = models.CharField(max_length=16, unique=True, default=generate_card_number)
    cvv = models.CharField(max_length=3, default=generate_cvv)
    expiry_date = models.DateField(default=default_expiry_date)
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.account.ownerName} - {self.card_number}"