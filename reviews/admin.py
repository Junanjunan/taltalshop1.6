from django.contrib import admin
from . import models
from items import models as items_models

class PhotoInline(admin.TabularInline):
    model = items_models.ItemPhoto

@admin.register(models.Review)
class AdminReview(admin.ModelAdmin):

    list_display = ('item', 'user', 'payment', 'rating', 'content', 'done', 'created')

    inlines = (PhotoInline,)
