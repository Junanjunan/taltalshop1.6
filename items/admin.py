from django.contrib import admin
from django.utils.html import mark_safe
from . import models


class PhotoInline(admin.TabularInline):
    model = models.ItemPhoto

class DetailPageInline(admin.TabularInline):
    model = models.ItemDetailPage


@admin.register(models.Item)
class AdminItems(admin.ModelAdmin):

    list_display = ('item_category', 'name', 'user', 'price', 'rocket', 'deli_fee', 'pay_count', 'rating', 'youtube_url','created',)
    inlines = (PhotoInline, DetailPageInline)

@admin.register(models.ItemPhoto)
class AdminItemsPhoto(admin.ModelAdmin):
    
    list_display = ('name', 'item', 'user', 'review')
    # list_display = ('name', 'item')

    def get_thumbnail(self, obj):
        return mark_safe(f'<img src="{obj.photo.url}" width="18px" />')

@admin.register(models.ItemDetailPage)
class AdminItemDetailPage(admin.ModelAdmin):

    list_display = ('name',  'item', 'user')


@admin.register(models.Inquiry)
class AdmminInquiry(admin.ModelAdmin):

    list_display = ('item', 'user', 'inquiry', 'comment')