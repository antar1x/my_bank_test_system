from django.urls import path

from bank import views
from django.contrib.auth.views import LogoutView

from bank.views import HomeView, CardsView

urlpatterns = [
    path('accounts/', views.AccountListView.as_view(), name='accounts'),
    path('transactions/', views.TransactionListView.as_view(), name='transactions'),
    path('transactions/create/', views.TransactionFormView.as_view(), name='transaction_create'),
    path('transfer/', views.TransferView.as_view(), name='transfer'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('', HomeView.as_view(), name='home'),
    path('cards/', CardsView.as_view(), name='cards'),
]
