import statistics
import datetime
from django.http.response import Http404
from django.shortcuts import render, redirect, reverse
from django.urls import reverse, reverse_lazy
from django.core.paginator import Paginator
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from . import models, forms
from users import models as users_models
from reviews import models as reviews_models


class LoggedInOnlyView(LoginRequiredMixin):
    login_url = reverse_lazy('users:login')


class ItemsListView(View):

    def get(self, request, *args, **kwargs):
        page = request.GET.get('page')
        item_list = models.Item.objects.all()
        paginator = Paginator(item_list, 12)
        items = paginator.get_page(page)
        return render(request, 'items/items_list.html', {'items': items, 'paginator': paginator})


class ItemDetailView(View):

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        item = models.Item.objects.get(pk=pk)
        inquiries = models.Inquiry.objects.all().order_by("-created")
        form = forms.InquiryCreatingForm()
        now = datetime.datetime.now()
        nowDatetime_id = now.strftime('%Y%m%d%H%M%S')
        if request.user.pk:
            new_id = str(nowDatetime_id) + str(request.user.pk) + str(item.pk)
        else:
            new_id = str(nowDatetime_id) + str(item.pk)
        review_list = reviews_models.Review.objects.filter(
            item=item, done=True).order_by("-created")
        rating_array = []
        for i in review_list:
            rating_array.append(i.rating)
        try:
            review_mean = round(statistics.mean(rating_array), 2)
            context = {
                'item': item,
                'inquiries': inquiries,
                'form': form,
                'new_id': new_id,
                'review_list': review_list,
                'review_mean': review_mean
            }
        except:
            context = {
                'item': item,
                'inquiries': inquiries,
                'form': form,
                'new_id': new_id,
                'review_list': review_list,
            }
        return render(request, 'items/item_detail.html', context)

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        form = forms.InquiryCreatingForm()
        item = models.Item.objects.get(pk=pk)
        inquiry = form.save()
        inquiry.item = item
        inquiry.user = request.user
        inquiry.inquiry = request.POST.get("inquiry")
        inquiry.save()
        return redirect(reverse("items:item-detail", kwargs={"pk": item.pk}))


class ItemCreatingView(LoggedInOnlyView, View):

    def get(self, request):
        form = forms.ItemCreatingForm
        return render(request, 'items/item_creating.html', {'form': form, })

    def post(self, request):
        files = request.FILES.getlist('file_field[]')
        for count, f in enumerate(files):
            form2 = forms.ItemPhotoCreatingForm()
            itemPhoto = form2.save()
            itemPhoto.user = request.user
            itemPhoto.photo = f
            itemPhoto.name = count
            itemPhoto.save()

        detail_pages = request.FILES.getlist('detail_pages')
        for count, f in enumerate(detail_pages):
            form3 = forms.ItemDetailPageCreatingForm()
            detail_page = form3.save()
            detail_page.user = request.user
            detail_page.photo = f
            detail_page.name = count
            detail_page.save()

        form = forms.ItemCreatingForm(request.POST)
        waiting_photos = models.ItemPhoto.objects.filter(
            item=None, user=request.user
        )
        waiting_detail_pages = models.ItemDetailPage.objects.filter(
            item=None, user=request.user
        )
        item = form.save()
        item.user = request.user
        item.save()
        for i in waiting_photos:
            i.item = item
            i.save()
        for i in waiting_detail_pages:
            i.item = item
            i.save()
        return redirect(reverse("items:item-detail", kwargs={"pk": item.pk}))


class ItemUpdatingView(LoggedInOnlyView, View):
    def get(self, request, *args, **kwargs):
        item_pk = kwargs.get("pk")
        item = models.Item.objects.get(pk=item_pk)
        form = forms.ItemUpdatingForm(instance=item)
        photos = item.photos.all()
        photo_form = forms.ItemPhotoMultipleCreatingForm()
        photo_form.queryset = photos
        context = {
            'form': form,
            'item': item,
            'photo_form': photo_form
        }
        return render(request, 'items/item_updating.html', context)

    def post(self, request, *args, **kwargs):
        item_pk = kwargs.get("pk")
        item = models.Item.objects.get(pk=item_pk)
        files = request.FILES.getlist('file_field[]')
        for count, f in enumerate(files):
            form2 = forms.ItemPhotoCreatingForm()
            itemPhoto = form2.save()
            itemPhoto.user = request.user
            itemPhoto.photo = f
            itemPhoto.name = count
            itemPhoto.save()
        detail_pages = request.FILES.getlist('detail_pages')
        for count, f in enumerate(detail_pages):
            form3 = forms.ItemDetailPageCreatingForm()
            detail_page = form3.save()
            detail_page.user = request.user
            detail_page.photo = f
            detail_page.name = count
            detail_page.save()

        form = forms.ItemUpdatingForm(request.POST, instance=item)
        waiting_photos = models.ItemPhoto.objects.filter(
            item=None, user=request.user)
        waiting_detail_pages = models.ItemDetailPage.objects.filter(
            item=None, user=request.user)
        item2 = form.save()
        item2.user = request.user
        item2.save()
        for i in waiting_photos:
            i.item = item
            i.save()
        for i in waiting_detail_pages:
            i.item = item
            i.save()
        return redirect(reverse("items:item-detail", kwargs={"pk": item.pk}))


@login_required
def delExImg(request, photo_pk):
    photo = models.ItemPhoto.objects.get(pk=photo_pk)
    if photo.user.pk == request.user.pk:
        photo.delete()
        return redirect(request.META['HTTP_REFERER'])


@login_required
def delExPage(request, page_pk):
    page = models.ItemDetailPage.objects.get(pk=page_pk)
    if page.user.pk == request.user.pk:
        page.delete()
        return redirect(request.META['HTTP_REFERER'])


@login_required
def pushBucket(request, item_pk):
    item = models.Item.objects.get(pk=item_pk)
    item_count = request.GET.get("item-count")
    if users_models.Bucket.objects.filter(user=request.user, item=item):
        existed_bucket = users_models.Bucket.objects.get(
            user=request.user, item=item)
        existed_bucket.item_count += int(item_count)
        existed_bucket.save()
    else:
        users_models.Bucket.objects.create(
            user=request.user, item=item, item_count=item_count, deli_fee=item.deli_fee)
    messages.success(request, "장바구니에 추가되었습니다.")
    return redirect(request.META['HTTP_REFERER'])


@login_required
def pushFav(request, item_pk):
    item = models.Item.objects.get(pk=item_pk)
    if users_models.Fav.objects.filter(user=request.user, item=item):
        users_models.Fav.objects.filter(user=request.user, item=item).delete()
    else:
        users_models.Fav.objects.create(
            user=request.user,
            item=item,
            item_count=1
        )
    return redirect(request.META['HTTP_REFERER'])


class ItemSearchView(View):
    def get(self, request):
        page = request.GET.get('page')
        name = request.GET.get("name")
        try:
            item_category = request.GET.get('category')
            filter_args = {}
            filter_args["name__contains"] = name
            filter_args["item_category__contains"] = item_category
            searched = models.Item.objects.filter(**filter_args)
        except:
            filter_args = {}
            filter_args["name__contains"] = name
            searched = models.Item.objects.filter(**filter_args)
        paginator = Paginator(searched, 12)
        items = paginator.get_page(page)
        return render(request, "items/search.html", {**filter_args, "items": items, "paginator": paginator})


class ItemLowPriceView(View):
    def get(self, request):
        page = request.GET.get("page")
        name = request.GET.get("name")
        try:
            item_category = request.GET.get('category')
            filter_args = {}
            filter_args["name__contains"] = name
            filter_args["item_category__contains"] = item_category
            searched = models.Item.objects.filter(
                **filter_args).order_by('price')
        except:
            filter_args = {}
            filter_args["name__contains"] = name
            searched = models.Item.objects.filter(
                **filter_args).order_by('price')
        paginator = Paginator(searched, 12)
        low_price_list = paginator.get_page(page)
        context = {
            **filter_args,
            "low_price_list": low_price_list,
            "paginator": paginator
        }
        return render(request, "items/search.html", context)


class ItemHighPriceView(View):
    def get(self, request):
        page = request.GET.get("page")
        name = request.GET.get("name")
        try:
            item_category = request.GET.get('category')
            filter_args = {}
            filter_args["name__contains"] = name
            filter_args["item_category__contains"] = item_category
            searched = models.Item.objects.filter(
                **filter_args).order_by('-price')
        except:
            filter_args = {}
            filter_args["name__contains"] = name
            searched = models.Item.objects.filter(
                **filter_args).order_by('-price')
        paginator = Paginator(searched, 12)
        high_price_list = paginator.get_page(page)
        context = {
            **filter_args,
            "high_price_list": high_price_list,
            "paginator": paginator
        }
        return render(request, "items/search.html", context)


class ItemPayCountView(View):
    def get(self, request):
        page = request.GET.get("page")
        name = request.GET.get("name")
        try:
            item_category = request.GET.get('category')
            filter_args = {}
            filter_args["name__contains"] = name
            filter_args["item_category__contains"] = item_category
            searched = models.Item.objects.filter(**filter_args).order_by('-pay_count')
        except:
            filter_args = {}
            filter_args["name__contains"] = name
            searched = models.Item.objects.filter(
                **filter_args).order_by('-pay_count')
        paginator = Paginator(searched, 12)
        pay_count_list = paginator.get_page(page)
        context = {
            **filter_args,
            "pay_count_list": pay_count_list,
            "paginator": paginator
        }
        return render(request, "items/search.html", context)


class ItemCreatedView(View):
    def get(self, request):
        page = request.GET.get("page")
        name = request.GET.get("name")
        try:
            item_category = request.GET.get('category')
            filter_args = {}
            filter_args["name__contains"] = name
            filter_args["item_category__contains"] = item_category
            searched = models.Item.objects.filter(
                **filter_args).order_by('-created')
        except:
            filter_args = {}
            filter_args["name__contains"] = name
            searched = models.Item.objects.filter(
                **filter_args).order_by('-created')
        paginator = Paginator(searched, 12)
        created_list = paginator.get_page(page)
        context = {
            **filter_args,
            "created_list": created_list,
            "paginator": paginator
        }
        return render(request, "items/search.html", context)


@login_required
def inquiry_comment(request, inquiry_pk):
    inquiry = models.Inquiry.objects.get(pk=inquiry_pk)
    inquiry.comment = request.GET.get("comment")
    inquiry.save()
    return redirect(request.META['HTTP_REFERER'])


@login_required
def inquiry_delete(request, inquiry_pk):
    inquiry = models.Inquiry.objects.get(pk=inquiry_pk)
    if inquiry.user.pk == request.user.pk:
        inquiry.delete()
        return redirect(request.META['HTTP_REFERER'])
    else:
        return Http404


@login_required
def inquiry_comment_delete(request, inquiry_pk):
    inquiry = models.Inquiry.objects.get(pk=inquiry_pk)
    inquiry.comment = None
    inquiry.save()
    return redirect(request.META['HTTP_REFERER'])
