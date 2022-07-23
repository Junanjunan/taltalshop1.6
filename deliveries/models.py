from django.db import models


class Delivery(models.Model):
    deli_number = models.CharField(max_length=50)
    deli_code = models.CharField(max_length=3)
    payment = models.ForeignKey("payments.Payment", related_name="deliveries", on_delete=models.CASCADE)
    done = models.BooleanField(default=False)