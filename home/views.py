from django.shortcuts import render
from django.views.generic import View
from . import models
from items import models as items_models

# Create your views here.
class HomeView(View):
    def get(self, request):
        photos = models.MainPhoto.objects.all()
        item_list = items_models.Item.objects.all()
        shampoo_list = items_models.Item.objects.filter(item_category = "shampoo")
        black_powder_list = items_models.Item.objects.filter(item_category = "black_powder")
        wig_list = items_models.Item.objects.filter(item_category = "wig")
        hairbeam_list = items_models.Item.objects.filter(item_category = "hairbeam")
        context = {
            'photos': photos,
            'item_list': item_list,
            'shampoo_list': shampoo_list,
            'black_powder_list': black_powder_list,
            'wig_list': wig_list,
            'hairbeam_list': hairbeam_list,
        }
        return render(request, 'home.html', context)


class ItemsHomeView(View):
    def get(self, request, *args, **kwargs):
        shampoo = models.Item.objects.get(item_category="샴푸")
        print(shampoo)
        context = {'shampoo': shampoo}
        return render(request, 'home:home', context)