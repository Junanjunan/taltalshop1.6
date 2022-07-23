from django.urls import path
from . import views

app_name = 'superuser'

urlpatterns = [
    path("main/", views.SuperuserMainView.as_view(), name="main"),
    path("payments/", views.SuperuserPaymentsView.as_view(), name="payments"),
    path("deliveries/<int:merchant_uid>/", views.SuperuserDeliveriesView.as_view(), name="deliveries"),
]
