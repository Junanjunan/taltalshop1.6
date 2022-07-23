import requests
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from . import models
from payments import models as payments_models

class LoggedInOnlyView(LoginRequiredMixin):
    login_url = reverse_lazy('users:login')

class DeliNumView(LoggedInOnlyView, View):
    def get(self, request, *args, **kwargs):
        merchant_uid = kwargs.get("merchant_uid")
        payment = payments_models.Payment.objects.get(merchant_uid=merchant_uid)
        try:
            delivery = models.Delivery.objects.get(payment = payment)
            return render(request, 'delivery/deli_num.html', {'delivery': delivery})
        except:
            return render(request, 'delivery/deli_num.html')

class DeliDetailView(LoggedInOnlyView, View):
    def get(self, request, *args, **kwargs):
        merchant_uid = kwargs.get("merchant_uid")
        payment = payments_models.Payment.objects.get(merchant_uid=merchant_uid)
        try:
            delivery = models.Delivery.objects.get(payment = payment)
            t_url = "http://info.sweettracker.co.kr/api/v1/trackingInfo"
            access_data = {
                't_key': settings.SWEETTRACKER_KEY,
                't_code': delivery.deli_code,
                't_invoice': delivery.deli_number
            }
            req = requests.get(t_url, params=access_data)
            t_res = req.json()
            print(t_res)
            return render(request, 'delivery/deli_detail.html', {'delivery': delivery, 't_res': t_res})
        except:
            return render(request, 'delivery/deli_detail.html')