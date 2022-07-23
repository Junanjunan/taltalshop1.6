from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
path("signup/", views.SignUpView.as_view(), name='signup'),
     path("signup/after/", views.SignUpAfterView.as_view(), name="signup-after"),
     path("verify/<str:key>", views.complete_verification,
          name="complete-verification"),
     path("login/", views.LoginView.as_view(), name='login'),
     path("login/github/", views.github_login, name="github-login"),
     path("login/github/callback/", views.github_callback, name="github-callback"),
     path("login/kakao/", views.kakao_login, name="kakao-login"),
     path("login/kakao/callback/", views.kakao_callback, name="kakao-callback"),
     path("login/naver/", views.naver_login, name="naver-login"),
     path("login/naver/callback/", views.naver_callback, name="naver-callback"),
     path("logout/", views.log_out, name="logout"),
     path("status/<int:pk>/", views.UserStatusView.as_view(), name="status"),
     path("changepassword/<int:pk>/",
          views.UpdatePasswordView.as_view(), name="change-password"),
     path("change-user-information/<int:pk>/", views.ChangeUserInformationView.as_view(), name="change-user-information"),
     path("change-address/<int:pk>/", views.ChangeAddressView.as_view(), name="change-address"),
     path("change-address-payment-creating/", views.ChangeAddressPaymentCreatingView.as_view(), name="change-address-payment-creating"),
     path("change-address-payment-updating/", views.ChangeAddressPaymentUpdatingView.as_view(), name="change-address-payment-updating"),
     path("item-seller-request/<int:pk>/", views.ItemSellerRequestView.as_view(), name="item-seller-request"),
     path("user_del/", views.user_del, name="user_del"),
     path("request-reset-link/", views.RequestPasswordResetEmail.as_view(),
          name="request-password"),
     path("set-new-password/<uidb64>/<token>/",
          views.CompletePasswordReset.as_view(), name="reset-user-password"),
     path("sending-password-email-done/", views.SendingPasswordEmailDone.as_view(),
          name="sending-passowrd-email-done"),

     path("customer-bucket/<int:pk>/",
          views.CustomerBucket.as_view(), name="customer-bucket"),
     path("customer-bucket/<int:pk>/delete/<int:bucket_pk>/",
          views.deleteBucket, name="delete-bucket"),
     path("customer-bucket/<int:pk>/change/", views.changeBucket, name="change-bucket"),          

     path("customer-payment-list/", views.CustomerPaymentListView.as_view(),
          name="customer-payment-list"),
     path("customer-payment-cancell-list/", views.CustomerPaymentCancellListView.as_view(),
          name="customer-payment-cancell-list"),

     path("customer-favs-list/", views.CustomerFavsList.as_view(),
          name="customer-favs-list"),

     path("customer-inquiry-list/", views.CustomerInquiryList.as_view(), name="customer-inquiry-list"),
     path("creating-another-address/", views.CreatingAnotherAddressView.as_view(), name="creating-another-address"),
     path("updating-another-address/<int:pk>/", views.UpdatingAnotherAddressView.as_view(), name="updating-another-address"),
     path("delete-another-address-payment/<int:pk>/", views.delete_another_address_payment, name="delete-another-address-payment"),
]
