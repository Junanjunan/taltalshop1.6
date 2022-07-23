from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
     path("direct/<int:merchant_uid>/<int:item_pk>/",
          views.PayDirectView.as_view(), name="direct"),
     path("save/", views.PaySaveView.as_view(), name="save"),
     path("select-address/<int:pk>/", views.SelectAddressView.as_view(), name="select-address"),
     path("direct/done/<int:merchant_uid>/",
          views.PayDoneView.as_view(), name="done"),
     path("cart/", views.PayCartView.as_view(), name="cart"),
     path("cart/save", views.PaySaveCartView.as_view(), name="cart-save"),
     path("cart/done/<int:merchant_uid>/",
          views.PayCartDoneView.as_view(), name="cart-done"),
     path("refund/", views.RefundView.as_view(), name="refund"),
     path("cart/refund/", views.RefundCartView.as_view(), name="cart-refund"),
     path("cart/partial-refund/<int:merchant_uid>/", views.RefundCartPartialView.as_view(), name="partial-refund"),
     path("asking-cancel/<int:merchant_uid>/", views.AskingCancelView.as_view(), name="asking-cancel")
]
