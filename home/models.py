from django.db import models

# Create your models here.
class MainPhoto(models.Model):
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
    main_photo = models.ImageField(upload_to="main_photo")
    name = models.CharField(max_length=100)
    