from django.contrib import admin
from bank.models import Account, Transaction, Transfer, Card

admin.site.register(Account)
admin.site.register(Transaction)
admin.site.register(Transfer)
admin.site.register(Card)