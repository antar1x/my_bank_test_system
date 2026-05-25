from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

from bank.models import Transaction, Account


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