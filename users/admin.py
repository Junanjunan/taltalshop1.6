from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models



@admin.register(models.User)
class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        ("Custom Profile",
            {"fields":
                ("avatar",
                 "phone_number",
                 "address",
                 "address_detail",
                 "login_method",
                 "email_verified",
                 "item_seller",
                 "item_seller_request",
                 "wig_shop_owner",
                 "hair_shop_owner",
                 "hospital_owner",
                 "tatoo_shop_owner",
                 "delivery_requirement",
                 "taltal_money"
                 )
             }
         ),
    )

    list_display = (
        'username',
        'first_name',
        'item_seller',
        "item_seller_request",
        "wig_shop_owner",
        "hair_shop_owner",
        "hospital_owner",
        "tatoo_shop_owner",
        'login_method',
        'email_verified',
        'email',
        'is_active',
        'is_staff',
        'is_superuser',
        'email_secret',
    )