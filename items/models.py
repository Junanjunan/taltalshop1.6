import os
import datetime
from django.db import models
from uuid import uuid4
from django_countries.fields import CountryField


class Item(models.Model):
    SHAMPOO = "shampoo"
    BLACK_POWDER = "black_powder"
    WIG = "wig"
    HAIR_BEAM = "hairbeam"

    ITEM_CATEGORY = (
        (SHAMPOO, "샴푸"),
        (BLACK_POWDER, "흑채"),
        (WIG, "가발"),
        (HAIR_BEAM, "헤어빔"),
    )

    item_category = models.CharField(max_length=30, choices=ITEM_CATEGORY)
    name = models.CharField(max_length=100)
    user = models.ForeignKey(
        "users.User", related_name="items", on_delete=models.CASCADE)
    price = models.PositiveIntegerField()
    deli_fee= models.PositiveIntegerField()
    rocket = models.BooleanField(default=False)
    pay_count = models.PositiveIntegerField(default=0)
    rating = models.FloatField(default=0)
    youtube_url = models.CharField(max_length=200, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    """common"""
    volume = models.FloatField(null=True, blank=True)
    specification = models.CharField(max_length=200, null=True, blank=True)
    use_period = models.CharField(max_length=100, null=True, blank=True)
    how_to_use = models.CharField(max_length=100, null=True, blank=True)
    producer = models.CharField(max_length=100, null=True, blank=True)
    coo = CountryField()
    cosmetic_component = models.TextField(null=True, blank=True)
    certification = models.CharField(max_length=100, null=True, blank=True)
    precaution = models.TextField(null=True, blank=True)
    quality_guarantee = models.CharField(max_length = 100, null=True, blank=True)
    """wig, hair_beam"""
    item_model_name = models.CharField(max_length=100, null=True, blank=True)
    about_electric = models.CharField(max_length=100, null=True, blank=True)
    release_date = models.CharField(max_length=20, null=True, blank=True)
    inquiry_number = models.CharField(max_length=30, null=True, blank=True)


    def __str__(self):
        return self.name

    def first_photo(self):
        try:
            photo, = self.photos.all()[:1]
            return photo.photo.url
        except ValueError:
            return None
    
    def second_photo(self):
        try:
            photo, = self.photos.all()[1:2]
            return photo.photo.url
        except ValueError:
            return None


def path_and_rename(instance, filename):
    file_origin_name = filename.split('.')[0]
    ext = filename.split('.')[-1]
    now = datetime.datetime.now()
    filename = '{}_{}_{}.{}'.format(file_origin_name, now,uuid4().hex, ext)
    return os.path.join(filename)

class ItemPhoto(models.Model):
    photo = models.ImageField(upload_to = path_and_rename)
    name = models.CharField(max_length=50, null=True, blank=True)
    item = models.ForeignKey("items.Item", related_name="photos", on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey("users.User", related_name="photos", on_delete=models.CASCADE)
    review = models.ForeignKey("reviews.Review", related_name="photos", on_delete=models.CASCADE, null=True, blank=True)

class ItemDetailPage(models.Model):
    photo = models.ImageField(upload_to = path_and_rename)
    name = models.CharField(max_length=50, null=True, blank=True)
    item = models.ForeignKey("items.Item", related_name="detail_pages", on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey("users.User", related_name="detail_pages", on_delete=models.CASCADE)

class Inquiry(models.Model):
    inquiry = models.TextField()
    user = models.ForeignKey("users.User", related_name="inquiries", on_delete=models.CASCADE)
    item = models.ForeignKey("items.Item", related_name="inquiries", on_delete=models.CASCADE)
    comment = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)