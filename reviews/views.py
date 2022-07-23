import statistics
from django.shortcuts import render, redirect, reverse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from . import models
from payments import models as payments_models
from items import models as items_models


class LoggedInOnlyView(LoginRequiredMixin):
    login_url = reverse_lazy('users:login')


class WaitingReviewList(LoggedInOnlyView, View):
    def get(self, request, *args, **kwargs):
        waiting_list = models.Review.objects.filter(
            user=request.user, done=False)
        return render(request, 'reviews/waiting_list.html', {'waiting_list': waiting_list})


class CreatingReview(LoggedInOnlyView, View):

    def get(self, request, *args, **kwargs):
        merchant_uid = kwargs.get("merchant_uid")
        payment = payments_models.Payment.objects.get(
            merchant_uid=merchant_uid)
        
        context =  {
            'payment': payment
            }
        return render(request, 'reviews/review_creating.html', context)

    def post(self, request, *args, **kwargs):
        merchant_uid = kwargs.get("merchant_uid")
        payment = payments_models.Payment.objects.get(
            merchant_uid=merchant_uid)
        item = payment.item
        user = payment.user
        review = models.Review.objects.create(payment=payment, item=item, user=user)
        
        rating_str = request.POST.get("rating")
        files = request.FILES.getlist('file')
        for count, f in enumerate(files):
            items_models.ItemPhoto.objects.create(
                photo=f,
                name=count,
                review=review,
                user=request.user
            )

        if rating_str == "two":
            rating_int = 2
        elif rating_str == "four":
            rating_int = 4
        elif rating_str == "six":
            rating_int = 6
        elif rating_str == "eight":
            rating_int = 8
        elif rating_str == "ten":
            rating_int = 10
        review.rating = rating_int
        review.content = request.POST.get("content")
        review.done = True
        review.save()

        review_list = models.Review.objects.filter(item=review.item, done=True)
        rating_array = []
        for i in review_list:
            rating_array.append(i.rating)

        review_mean = round(statistics.mean(rating_array), 2)

        item = items_models.Item.objects.get(pk=review.item.pk)
        item.rating = review_mean
        item.save()
        return redirect(reverse("items:item-detail", kwargs={"pk": review.item.pk}))


class UpdatingReview(LoggedInOnlyView, View):
    def get(self, request, *args, **kwargs):
        merchant_uid = kwargs.get("merchant_uid")
        payment = payments_models.Payment.objects.get(merchant_uid=merchant_uid)
        review = payment.reviews
        context = {
            'review': review
        }
        return render(request, 'reviews/review_updating.html', context)

    def post(self, request, *args, **kwargs):
        merchant_uid = kwargs.get("merchant_uid")
        payment = payments_models.Payment.objects.get(merchant_uid=merchant_uid)
        review = payment.reviews
        rating_str = request.POST.get("rating")
        files = request.FILES.getlist('file')
        for count, f in enumerate(files):
            items_models.ItemPhoto.objects.create(
                photo=f,
                name=count,
                review=review,
                user=request.user
            )
        if rating_str == "two":
            rating_int = 2
        elif rating_str == "four":
            rating_int = 4
        elif rating_str == "six":
            rating_int = 6
        elif rating_str == "eight":
            rating_int = 8
        elif rating_str == "ten":
            rating_int = 10
        review.rating = rating_int
        review.content = request.POST.get("content")
        review.done = True
        review.save()

        review_list = models.Review.objects.filter(item=review.item, done=True)
        rating_array = []
        
        for i in review_list:
            rating_array.append(i.rating)
        
        review_mean = round(statistics.mean(rating_array), 2)
        item = items_models.Item.objects.get(pk=review.item.pk)
        item.rating = review_mean
        item.save()

        context = {
            'review': review
        }
        return redirect(reverse("items:item-detail", kwargs={"pk": review.item.pk}))

class PersonalReviewList(LoggedInOnlyView, View):
    def get(self, request, *args, **kwargs):
        review_list = models.Review.objects.filter(
            user=request.user, done=True)
        return render(request, 'reviews/personal_reviews.html', {'review_list': review_list})
