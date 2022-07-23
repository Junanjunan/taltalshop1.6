from django.shortcuts import render, redirect, reverse
from django.views.generic import View
from django.http import Http404
from django.core.paginator import Paginator
from payments import models as payments_models
from deliveries import models as deliveries_models


class SuperuserMainView(View):
    def get(self, request):
        if request.user.is_superuser:
            return render(request, 'superuser/main.html')
        else:
            return Http404


class SuperuserPaymentsView(View):
    def get(self, request):
        if request.user.is_superuser:
            page = request.GET.get('page')
            payments_list = payments_models.Payment.objects.filter(status="paid").order_by("-created")
            paginator = Paginator(payments_list, 5)
            items = paginator.get_page(page)
            context = {'items': items, 'paginator': paginator}
            return render(request, 'superuser/payments.html', context)
        else:
            return Http404


class SuperuserDeliveriesView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            merchant_uid = kwargs.get("merchant_uid")
            payment = payments_models.Payment.objects.get(merchant_uid=merchant_uid)
            
            context = {
                'payment': payment,
            }

            return render(request, 'superuser/deliveries.html', context)
        else:
            return Http404

    def post(self, request, *args, **kwargs):
        if request.user.is_superuser:
            merchant_uid = kwargs.get("merchant_uid")
            deli_code = request.POST.get("deli_code")
            deli_number = request.POST.get("deli_number")
            
            payment = payments_models.Payment.objects.get(merchant_uid=merchant_uid)
            if deliveries_models.Delivery.objects.filter(payment=payment):
                ex_deli = deliveries_models.Delivery.objects.get(payment=payment)
                ex_deli.deli_code = deli_code
                ex_deli.deli_number = deli_number
                ex_deli.save()
            else:
                deliveries_models.Delivery.objects.create(deli_number=deli_number, deli_code=deli_code, payment=payment)
            
            context = {
                'payment': payment,
            }

            return redirect(reverse("superuser:payments"))
        else:
            return Http404