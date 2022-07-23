from django.urls import path
from . import views

app_name = 'items'

urlpatterns = [
     path("", views.ItemsListView.as_view(), name="items-list"),
    path("<int:pk>/", views.ItemDetailView.as_view(), name="item-detail"),
    path("creating/", views.ItemCreatingView.as_view(), name="item-creating"),
    path("updating/<int:pk>/", views.ItemUpdatingView.as_view(), name="item-updating"),
    path("photo-delete/<int:photo_pk>/", views.delExImg, name="exphoto-delete"),
    path("page-delete/<int:page_pk>/", views.delExPage, name="expage-delete"),
    path("<int:item_pk>/pushbucket/", views.pushBucket, name="push-item"),
    path("<int:item_pk>/pushfav/", views.pushFav, name="push-fav"),
    path("search/", views.ItemSearchView.as_view(), name="search"),
    path("search/low-price/", views.ItemLowPriceView.as_view(), name="low-price"),
    path("search/high-price/", views.ItemHighPriceView.as_view(), name="high-price"),
    path("search/pay-count", views.ItemPayCountView.as_view(), name="pay-count"),
    path("search/created", views.ItemCreatedView.as_view(), name="created"),
    path("inquiry-comment/<int:inquiry_pk>/",
         views.inquiry_comment, name="inquiry-comment"),
    path("inquiry-delete/<int:inquiry_pk>/",
         views.inquiry_delete, name="inquiry-delete"),
    path("inquiry-comment-delete/<int:inquiry_pk>",
         views.inquiry_comment_delete, name="inquiry-comment-delete"),
]
