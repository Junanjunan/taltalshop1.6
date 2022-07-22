from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

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