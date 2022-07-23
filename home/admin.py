from django.contrib import admin
from django.utils.html import mark_safe
from . import models


@admin.register(models.MainPhoto)
class MainPhotoAdmin(admin.ModelAdmin):

    list_display=('item_category', 'name', 'get_thumbnail')

    def get_thumbnail(self, obj):
        return mark_safe(f'<img src="{obj.main_photo.url}" width="18px" />')