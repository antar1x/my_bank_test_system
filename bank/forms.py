from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

from bank.models import Transaction, Account, Card


class TransactionsForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['account', 'transaction_type', 'amount', 'description']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['account'].queryset = Account.objects.filter(user=user)


class TransferForm(forms.Form):
    from_account = forms.ModelChoiceField(queryset=Account.objects.none())
    to_account = forms.ModelChoiceField(queryset=Account.objects.none())
    amount = forms.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    description = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        accounts = Account.objects.filter(user=user)
        self.fields['from_account'].queryset = accounts
        self.fields['to_account'].queryset = accounts

    def clean(self):
        cleaned_data = super().clean()

        from_account = cleaned_data.get('from_account')
        to_account = cleaned_data.get('to_account')
        amount = cleaned_data.get('amount')

        if from_account and to_account and from_account == to_account:
            raise forms.ValidationError("Choose different accounts")

        if from_account and amount and from_account.balance < amount:
            raise forms.ValidationError("Not enough money")

        return cleaned_data

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['account']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['account'].queryset = Account.objects.filter(user=user)

class DifferentTransferForm(forms.Form):
    from_account = forms.ModelChoiceField(queryset=Account.objects.none())
    to_card_number = forms.CharField(max_length=16)
    amount = forms.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    description = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        accounts = Account.objects.filter(user=user)
        self.fields['from_account'].queryset = accounts

    def clean(self):
        cleaned_data = super().clean()

        from_account = cleaned_data.get('from_account')
        to_card_number = cleaned_data.get('to_card_number')
        amount = cleaned_data.get('amount')
        if to_card_number:
            to_card = Card.objects.filter(card_number=to_card_number, is_active=True).first()

            if not to_card:
                raise forms.ValidationError("Card not found")

            cleaned_data["to_card"] = to_card
            cleaned_data["to_account_obj"] = to_card.account

            if from_account and to_card.account == from_account:
                raise forms.ValidationError("You cannot transfer to the same account")

        if from_account and amount and from_account.balance < amount:
            raise forms.ValidationError("Not enough money")

        return cleaned_data
