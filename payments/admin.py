from django.contrib import admin
from . import models
from reviews import models as reviews_models


class ReviewInline(admin.TabularInline):
    model = reviews_models.Review

@admin.register(models.Payment)
class AdminPayment(admin.ModelAdmin):

    list_display = (
        'merchant_uid',
        'imp_uid',
        'user',
        'item',
        'price',
        'item_count',
        'deli_fee',
        'paid_amount',
        'pay_method',
        'receiver',
        'address',
        'phone_number',
        'email',
        'require',
        'status',
        'created',
        'bucket_paid',
    )

    inlines = (ReviewInline,)


class PaymentInline(admin.TabularInline):
    model = models.Payment


@admin.register(models.BucketPayment)
class AdminBucketPayment(admin.ModelAdmin):

    list_display = (
        'imp_uid',
        'merchant_uid',
        'user',
        'paid_amount',
        'pay_method',
        'status',
        'created',
    )

    inlines = (PaymentInline,)
