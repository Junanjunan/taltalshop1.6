import uuid
from django.conf import settings
from django.db import models
from django.contrib import messages
from django.contrib.auth.models import AbstractUser
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.html import strip_tags


class User(AbstractUser):
    LOGIN_EMAIL = "email"
    LOGIN_GITHUB = "github"
    LOGIN_KAKAO = "kakao"
    LOGIN_NAVER = "naver"
    LOGIN_CHOICES = (
        (LOGIN_EMAIL, "Email"),
        (LOGIN_GITHUB, "Github"),
        (LOGIN_KAKAO, "Kakao"),
        (LOGIN_NAVER, "Naver")
    )

    login_method = models.CharField(
        max_length=50, choices=LOGIN_CHOICES, default=LOGIN_EMAIL)
    avatar = models.ImageField(upload_to="avatars", blank=True)
    phone_number = models.CharField(max_length=25, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    address_detail = models.CharField(max_length=100, blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    email_secret = models.CharField(max_length=20, default="", blank=True)
    item_seller = models.BooleanField(default=False)
    item_seller_request = models.BooleanField(default=False)
    wig_shop_owner = models.BooleanField(default=False)
    hair_shop_owner = models.BooleanField(default=False)
    hospital_owner = models.BooleanField(default=False)
    tatoo_shop_owner = models.BooleanField(default=False)
    delivery_requirement = models.CharField(
        max_length=150, null=True, blank=True)
    taltal_money = models.PositiveBigIntegerField(
        default=0, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)

    def verify_email(self):
        if self.email_verified is False:
            secret = uuid.uuid4().hex[:20]
            self.email_secret = secret
            if settings.DEBUG == True:
                html_message = render_to_string(
                    "emails/verify_email_dev.html", {"secret": secret}
                )
            else:
                html_message = render_to_string(
                    "emails/verify_email_deploy.html", {"secret": secret}
                )
            send_mail(
                "탈탈샵 회원가입 인증 메일입니다.",
                strip_tags(html_message),
                settings.EMAIL_HOST_USER,
                [self.email],
                fail_silently=False,
                html_message=html_message,
            )
            self.save()
        else:
            messages.error(self.request, "E!!!!!")


class Bucket(models.Model):
    user = models.ForeignKey(
        "User", related_name="totalbuckets", on_delete=models.CASCADE)
    item = models.ForeignKey(
        "items.Item", related_name="totalbuckets", on_delete=models.CASCADE)
    item_count = models.PositiveIntegerField()
    deli_fee = models.PositiveIntegerField()

    def price(self):
        price = self.item.price
        return price

    def total_price(self):
        total_price = self.item.price * self.item_count
        return total_price


class Fav(models.Model):
    user = models.ForeignKey(
        "User", related_name="favs", on_delete=models.CASCADE)
    item = models.ForeignKey(
        "items.Item", related_name="favs", on_delete=models.CASCADE)
    item_count = models.PositiveIntegerField(default=1)

    def price(self):
        price = self.item.price
        return price

    def deli_fee(self):
        deli_fee = self.item.deli_fee
        return deli_fee

    def __str__(self):
        return self.item.name

class AnotherAddress(models.Model):
    user = models.ForeignKey("User", related_name="another_addresses", on_delete=models.CASCADE)
    receiver = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=25)
    address = models.CharField(max_length=100)
    address_detail = models.CharField(max_length=100)
    delivery_requirement = models.CharField(max_length=150, null=True, blank=True)