from django.contrib import admin
from . import models


@admin.register(models.Delivery)
class AdminDelivery(admin.ModelAdmin):

    list_display = ('deli_number', 'deli_code', 'payment','done')
