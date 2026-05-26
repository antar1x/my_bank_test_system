from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.db import transaction
from django.contrib.auth.forms import AuthenticationForm

from bank.errors import NotEnoughBalance
from bank.models import Account, Transaction, Transfer, Card
from bank.forms import TransactionsForm, TransferForm, RegisterForm, CardForm, DifferentTransferForm


class AccountListView(LoginRequiredMixin, View):
    def get(self, request):
        accounts = Account.objects.filter(user=request.user)

        return render(request, 'accounts.html', {
            'accounts': accounts
        })

class TransactionListView(LoginRequiredMixin, View):
    def get(self, request):
        transactions = Transaction.objects.filter(account__user=request.user).order_by("-date_created")
        return render(request, 'transactions.html', {
            'transactions': transactions
        })

class TransactionFormView(LoginRequiredMixin, View):
    def get(self, request):
        form = TransactionsForm(user=request.user)
        return render(request, 'transactioncreate.html', {'form': form})
    def post(self, request):
        form = TransactionsForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                form.save()
                return redirect("transactions")
            except NotEnoughBalance as error:
                form.add_error(None, error)
        return render(request, "transactioncreate.html", {"form": form})


class TransferView(LoginRequiredMixin, View):
    def get(self, request):
        form = TransferForm(user=request.user)
        return render(request, 'transfer.html', {'form': form})

    def post(self, request):
        form = TransferForm(request.POST, user=request.user)

        if form.is_valid():
            from_account = form.cleaned_data["from_account"]
            to_account = form.cleaned_data["to_account"]
            amount = form.cleaned_data["amount"]

            with transaction.atomic():
                from_account.balance -= amount
                to_account.balance += amount
                from_account.save()
                to_account.save()

            Transfer.objects.create(
                from_account=from_account,
                to_account=to_account,
                amount=amount,
                description=form.cleaned_data["description"]
            )

            return redirect("accounts")

        return render(request, "transfer.html", {"form": form})


class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, "register.html", {"form": form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect('login')

        else:
            return render(request, 'register.html', {"form": form})

class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'login.html', {"form": form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            login(request, user)

            return redirect("accounts")

        return render(request, 'login.html', {"form": form})

class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'home.html')

class CardsView(LoginRequiredMixin, View):
    def get(self, request):
        cards = Card.objects.filter(account__user=request.user)
        return render(request, 'cards.html', {"cards": cards})

class CardCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = CardForm(user=request.user)
        return render(request, 'cardcreate.html', {"form": form})
    def post(self, request):
        form = CardForm(request.POST, user=request.user)

        if form.is_valid():
            form.save()
            return redirect("cards")

        return render(request, "cardcreate.html", {"form": form})

class DifferentTransferView(LoginRequiredMixin, View):
    def get(self, request):
        form = DifferentTransferForm(user=request.user)
        return render(request, 'cardtransfer.html', {"form": form})

    def post(self, request):
        form = DifferentTransferForm(request.POST, user=request.user)

        if form.is_valid():
            from_account = form.cleaned_data["from_account"]
            to_account = form.cleaned_data["to_account_obj"]
            amount = form.cleaned_data["amount"]

            with transaction.atomic():
                from_account.balance -= amount
                to_account.balance += amount
                from_account.save()
                to_account.save()

                Transfer.objects.create(
                    from_account=from_account,
                    to_account=to_account,
                    amount=amount,
                    description=form.cleaned_data["description"],
                )

            return redirect("accounts")

        return render(request, "cardtransfer.html", {"form": form})

