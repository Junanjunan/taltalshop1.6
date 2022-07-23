from django.db import models


class Payment(models.Model):
    merchant_uid = models.CharField(max_length=120, unique=True)
    imp_uid = models.CharField(max_length=120, null=True, blank=True)
    user = models.ForeignKey(
        "users.User", related_name="payments", on_delete=models.CASCADE)
    item = models.ForeignKey(
        "items.Item", related_name="payments", on_delete=models.PROTECT)
    price = models.PositiveIntegerField()
    item_count = models.PositiveIntegerField()
    deli_fee = models.PositiveIntegerField()
    paid_amount = models.PositiveIntegerField(default=0)
    pay_method = models.CharField(max_length=120)
    receiver = models.CharField(max_length = 30)
    address = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.CharField(max_length=100, null=True, blank=True)
    require = models.CharField(max_length=40)
    status = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    bucket_paid = models.ForeignKey(
        "BucketPayment", related_name="payments", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.merchant_uid


class BucketPayment(models.Model):
    user = models.ForeignKey(
        "users.User",  related_name="buketpayments", on_delete=models.CASCADE)
    imp_uid = models.CharField(max_length=120, null=True, blank=True)
    merchant_uid = models.CharField(max_length=120, unique=True)
    paid_amount = models.PositiveIntegerField(default=0)
    pay_method = models.CharField(max_length=120)
    status = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __str__(self):
        return self.imp_uid
