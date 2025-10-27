from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.finance_dashboard, name='dashboard'),
    path('payment/', views.fee_payment, name='payment'),
    path('invoices/', views.invoice_list, name='invoices'),
]
