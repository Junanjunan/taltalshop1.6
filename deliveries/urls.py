from django.urls import path
from . import views

app_name = 'deliveries'

urlpatterns = [
    path("<int:merchant_uid>/", views.DeliNumView.as_view(), name="deli-num"),
    path("<int:merchant_uid>/detail/", views.DeliDetailView.as_view(), name="deli-detail"),
]
