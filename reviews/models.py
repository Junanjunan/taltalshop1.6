from django.db import models


class Review(models.Model):
    item = models.ForeignKey("items.Item", related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", related_name="reviews", on_delete=models.CASCADE)
    payment = models.OneToOneField("payments.Payment", related_name="reviews", on_delete=models.CASCADE, null=True)
    rating = models.PositiveIntegerField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    done = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)