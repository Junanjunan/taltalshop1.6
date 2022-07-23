from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path("waiting-list/", views.WaitingReviewList.as_view(), name="waiting-list"),
    path("creating-review/<int:merchant_uid>/", views.CreatingReview.as_view(), name="creating-review"),
    path("updating-review/<int:merchant_uid>/", views.UpdatingReview.as_view(), name="updating-review"),
    path("personal-reviews/", views.PersonalReviewList.as_view(), name="personal-reviews"),
]