import requests
import datetime
from django.http import Http404
from django.http.response import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.conf import settings
from . import models
from items import models as items_models
from users import models as users_models


class LoggedInOnlyView(LoginRequiredMixin):
    login_url = reverse_lazy('users:login')


class SelectAddressView(LoggedInOnlyView, View):
    def get(self, request, *args, **kwargs):
        user_pk = kwargs.get("pk")
        user = users_models.User.objects.get(pk=user_pk)
        address_list = users_models.AnotherAddress.objects.filter(user = user)
        context = {
            'address_list': address_list
        }
        return render(request, 'payment/select_address.html', context)

class PayDirectView(LoggedInOnlyView, View):
    def get(self, request, *args, **kwargs):
        merchant_uid = kwargs.get('merchant_uid')
        item_pk = kwargs.get('item_pk')
        item = items_models.Item.objects.get(pk=item_pk)
        item_count = request.GET.get("item-count")
        amount = int(item.price) * int(item_count)
        amount_with_deli = amount + int(item.deli_fee)
        return render(request, 'payment/direct.html', {'merchant_uid': merchant_uid, 'item': item, 'item_count': item_count, 'amount': amount, 'amount_with_deli': amount_with_deli})


class PaySaveView(LoggedInOnlyView, View):
    def post(self, request):
        user = request.user
        imp_uid = request.POST.get("imp_uid")
        merchant_uid = request.POST.get("merchant_uid")
        name = request.POST.get("name")
        item_pk = request.POST.get("item_pk")
        item = items_models.Item.objects.get(pk=item_pk)
        price = item.price
        deli_fee = item.deli_fee
        item_count = request.POST.get("item_count")
        paid_amount = request.POST.get('paid_amount')
        pay_method = request.POST.get('pay_method')
        receiver = request.POST.get('receiver')
        address = request.POST.get('address')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        require = request.POST.get('require')

        token_access_data = {
            'imp_key': settings.IAMPORT_KEY,
            'imp_secret': settings.IAMPORT_SECRET
        }

        token_url = "https://api.iamport.kr/users/getToken"
        req = requests.post(token_url, data=token_access_data)
        token_access_res = req.json()
        access_token = token_access_res['response']['access_token']

        """"""
        prepare_access_data = {
            'merchant_uid': merchant_uid,
            'amount': paid_amount
        }

        prepare_url = "https://api.iamport.kr/payments/prepare"

        headers = {
            'Authorization': access_token
        }

        prepare_req = requests.post(
            prepare_url, data=prepare_access_data, headers=headers)
        prepare_res = prepare_req.json()

        prepare_merchant_uid = prepare_res['response']['merchant_uid']
        prepare_amount = prepare_res['response']['amount']

        """"""

        find_url = "https://api.iamport.kr/payments/find/" + merchant_uid
        find_req = requests.post(find_url, headers=headers)
        find_res = find_req.json()

        find_merchant_uid = find_res['response']['merchant_uid']
        find_amount = find_res['response']['amount']

        context = {
            'imp_uid': find_res['response']['imp_uid'],
            'merchant_uid': find_res['response']['merchant_uid'],
            'amount': find_res['response']['amount'],
            'status': find_res['response']['status'],
            'pay_method': find_res['response']['pay_method'],
            'receipt_url': find_res['response']['receipt_url'],
        }

        if find_res['code'] == 0 and prepare_merchant_uid == find_merchant_uid:
            if prepare_amount == find_amount:
                payment = models.Payment.objects.create(
                    user=user,
                    item=item,
                    imp_uid=imp_uid,
                    merchant_uid=merchant_uid,
                    price=price,
                    item_count=item_count,
                    deli_fee=deli_fee,
                    paid_amount=paid_amount,
                    pay_method=pay_method,
                    receiver = receiver,
                    address = address,
                    email = email,
                    phone_number = phone_number,
                    require = require,
                    status=find_res['response']['status']
                )
                item.pay_count = int(item.pay_count) + int(item_count)
                item.save()
                data = context
                return JsonResponse(data)
            else:
                print("결제 금액에 문제가 존재")
                cancel_data = {
                    'merchant_uid': merchant_uid
                }

                cancel_url = "https://api.iamport.kr/payments/cancel/"
                requests.post(cancel_url, headers=headers, data=cancel_data)
                return None
        else:
            print("주문번호상에 문제가 존재")
            cancel_data = {
                'merchant_uid': merchant_uid
            }

            cancel_url = "https://api.iamport.kr/payments/cancel/"
            requests.post(cancel_url, headers=headers, data=cancel_data)
            return None


class PayDoneView(LoggedInOnlyView, View):
    def get(self, request, *args, **kwargs):
        payment = models.Payment.objects.get(
            merchant_uid=kwargs.get("merchant_uid"))
        pxq = payment.item.price * payment.item_count
        context = {
            'payment': payment,
        }
        return render(request, 'payment/direct_done.html', context)


"""Cart Payment"""


class PayCartView(LoggedInOnlyView, View):
    def get(self, request, *args, **kwargs):
        now = datetime.datetime.now()
        nowDatetime_id = now.strftime('%Y%m%d%H%M%S')
        merchant_uid = str(nowDatetime_id) + str(request.user.pk)
        bucket = users_models.Bucket.objects.filter(user=request.user)
        first_item = bucket[0].item
        item_amount = 0
        deli_fee_amount = 0
        for item in bucket:
            item_amount += int(item.total_price())
            deli_fee_amount += int(item.item.deli_fee)
        total_amount = item_amount + deli_fee_amount
        return render(
            request,
            'payment/cart.html',
            {
                'merchant_uid': merchant_uid,
                'bucket': bucket,
                'first_item': first_item,
                'item_amount': item_amount,
                'deli_fee_amount': deli_fee_amount,
                'total_amount': total_amount
            }
        )


class PaySaveCartView(LoggedInOnlyView, View):
    def post(self, request):
        user = request.user
        imp_uid = request.POST.get("imp_uid")
        merchant_uid = request.POST.get("merchant_uid")
        paid_amount = request.POST.get('paid_amount')
        pay_method = request.POST.get('pay_method')
        name = request.POST.get("name")

        token_access_data = {
            'imp_key': settings.IAMPORT_KEY,
            'imp_secret': settings.IAMPORT_SECRET
        }

        token_url = "https://api.iamport.kr/users/getToken"
        req = requests.post(token_url, data=token_access_data)
        token_access_res = req.json()
        access_token = token_access_res['response']['access_token']

        """"""
        prepare_access_data = {
            'merchant_uid': merchant_uid,
            'amount': paid_amount
        }

        prepare_url = "https://api.iamport.kr/payments/prepare"

        headers = {
            'Authorization': access_token
        }

        prepare_req = requests.post(
            prepare_url, data=prepare_access_data, headers=headers)
        prepare_res = prepare_req.json()

        prepare_merchant_uid = prepare_res['response']['merchant_uid']
        prepare_amount = prepare_res['response']['amount']

        """"""
        find_url = "https://api.iamport.kr/payments/find/" + merchant_uid
        find_req = requests.post(find_url, headers=headers)
        find_res = find_req.json()

        find_merchant_uid = find_res['response']['merchant_uid']
        find_amount = find_res['response']['amount']

        context = {
            'imp_uid': find_res['response']['imp_uid'],
            'merchant_uid': find_res['response']['merchant_uid'],
            'amount': find_res['response']['amount'],
            'status': find_res['response']['status'],
            'pay_method': find_res['response']['pay_method'],
            'receipt_url': find_res['response']['receipt_url'],
        }

        if find_res['code'] == 0 and prepare_merchant_uid == find_merchant_uid:
            if prepare_amount == find_amount:

                new_bucket_payment = models.BucketPayment.objects.create(
                    user=user,
                    imp_uid=imp_uid,
                    merchant_uid=merchant_uid,
                    paid_amount=paid_amount,
                    pay_method=pay_method,
                    status=find_res['response']['status']
                )
                data = context

                bucket = users_models.Bucket.objects.filter(user=request.user)
                for order in bucket:
                    payment = models.Payment.objects.create(
                        user=user,
                        item=order.item,
                        item_count=order.item_count,
                        merchant_uid=str(merchant_uid) + str(order.item.pk),
                        price=order.price(),
                        deli_fee=order.deli_fee,
                        paid_amount=int(order.total_price()) +
                        int(order.deli_fee),
                        pay_method=pay_method,
                        status=find_res['response']['status'],
                        bucket_paid=new_bucket_payment
                    )
                    item = items_models.Item.objects.get(pk=payment.item.pk)
                    item.pay_count = int(item.pay_count) + \
                        int(order.item_count)
                    item.save()
                users_models.Bucket.objects.filter(user=request.user).delete()

                return JsonResponse(data)
            else:
                print("결제 금액에 문제가 존재")
                cancel_data = {
                    'merchant_uid': merchant_uid
                }

                cancel_url = "https://api.iamport.kr/payments/cancel/"
                requests.post(cancel_url, headers=headers, data=cancel_data)
                return None
        else:
            print("주문번호상에 문제가 존재")
            cancel_data = {
                'merchant_uid': merchant_uid
            }

            cancel_url = "https://api.iamport.kr/payments/cancel/"
            requests.post(cancel_url, headers=headers, data=cancel_data)
            return None


class PayCartDoneView(LoggedInOnlyView, View):
    def get(self, request, *args, **kwargs):
        bucket_payment = models.BucketPayment.objects.get(
            merchant_uid=kwargs.get("merchant_uid")
        )
        each_payment = models.Payment.objects.filter(
            bucket_paid=bucket_payment)
        first_payment = each_payment[0]
        context = {
            'bucket_payment': bucket_payment,
            'each_payment': each_payment,
            'first_payment': first_payment
        }
        return render(request, 'payment/cart_done.html', context)


"""Cancel Payment"""


class RefundView(LoggedInOnlyView, View):
    def post(self, request):
        merchant_uid = request.POST.get("merchant_uid")
        if request.user.is_staff or request.user.pk == models.Payment.objects.get(merchant_uid=merchant_uid).user.pk:

            """액세스 토큰 발급"""
            token_access_data = {
                'imp_key': settings.IAMPORT_KEY,
                'imp_secret': settings.IAMPORT_SECRET
            }

            token_url = "https://api.iamport.kr/users/getToken"
            req = requests.post(token_url, data=token_access_data)
            token_access_res = req.json()
            access_token = token_access_res['response']['access_token']

            """결제 정보 조회"""

            headers = {
                'Authorization': access_token
            }

            cancel_data = {
                'merchant_uid': merchant_uid
            }

            cancel_url = "https://api.iamport.kr/payments/cancel/"
            cancel_req = requests.post(
                cancel_url, headers=headers, data=cancel_data)
            cancel_res = cancel_req.json()

            """cancel database"""

            cancel_imp_uid = cancel_res['response']['imp_uid']

            cancelled_payment = models.Payment.objects.get(
                imp_uid=cancel_imp_uid)
            cancelled_payment.status = cancel_res['response']['status']
            cancelled_payment.save()
            item = items_models.Item.objects.get(pk=cancelled_payment.item.pk)
            item.pay_count = int(item.pay_count) - \
                int(cancelled_payment.item_count)
            item.save()

            context = {
                'code': cancel_res['code'],
                'imp_uid': cancel_res['response']['imp_uid'],
                'merchant_uid': cancel_res['response']['merchant_uid'],
                'name': cancel_res['response']['name'],
                'pay_method': cancel_res['response']['pay_method'],
                'amount': cancel_res['response']['amount'],
                'status': cancel_res['response']['status'],
            }

            data = context

            return JsonResponse(data)
        else:
            print("환불 권한이 없는 유저입니다.")
            raise Http404


class RefundCartView(LoggedInOnlyView, View):
    def post(self, request):
        merchant_uid = request.POST.get("merchant_uid")
        if request.user.is_staff or request.user.pk == models.BucketPayment.objects.get(merchant_uid=merchant_uid).user.pk:
            """액세스 토큰 발급"""
            token_access_data = {
                'imp_key': settings.IAMPORT_KEY,
                'imp_secret': settings.IAMPORT_SECRET
            }

            token_url = "https://api.iamport.kr/users/getToken"
            req = requests.post(token_url, data=token_access_data)
            token_access_res = req.json()
            access_token = token_access_res['response']['access_token']

            """결제 정보 조회"""

            headers = {
                'Authorization': access_token
            }

            cancel_data = {
                'merchant_uid': merchant_uid
            }

            cancel_url = "https://api.iamport.kr/payments/cancel/"
            cancel_req = requests.post(
                cancel_url, headers=headers, data=cancel_data)
            cancel_res = cancel_req.json()

            """cancel database"""

            cancel_imp_uid = cancel_res['response']['imp_uid']
            bucket_payment = models.BucketPayment.objects.get(
                imp_uid=cancel_imp_uid
            )
            cancelled_payment = models.Payment.objects.filter(
                bucket_paid=bucket_payment)
            for p in cancelled_payment:
                p.status = cancel_res['response']['status']
                p.save()
                item = items_models.Item.objects.get(pk=p.item.pk)
                item.pay_count = int(item.pay_count) - int(p.item_count)
                item.save()

            cancelled_bucket_payment = models.BucketPayment.objects.get(
                imp_uid=cancel_imp_uid
            )
            cancelled_bucket_payment.status = cancel_res['response']['status']
            cancelled_bucket_payment.save()
            context = {
                'code': cancel_res['code'],
                'merchant_uid': cancel_res['response']['merchant_uid'],
                'pay_method': cancel_res['response']['pay_method'],
                'amount': cancel_res['response']['amount'],
                'status': cancel_res['response']['status'],
            }

            data = context

            return JsonResponse(data)
        else:
            print("환불 권한이 없는 유저입니다.")
            return Http404


class RefundCartPartialView(LoggedInOnlyView, View):
    def get(self, request, *args, **kwargs):
        item_merchant_uid = kwargs.get("merchant_uid")
        payment = models.Payment.objects.get(merchant_uid=item_merchant_uid)
        #direct_pay = models.Payment.objects.get(merchant_uid = item_merchant_uid).imp_uid
        # print(direct_pay)
        return render(request, "payment/partial_refund.html", {"payment": payment})

    def post(self, request, *args, **kwargs):
        if request.user.is_staff:
            item_merchant_uid = kwargs.get("merchant_uid")
            """액세스 토큰 발급"""
            token_access_data = {
                'imp_key': settings.IAMPORT_KEY,
                'imp_secret': settings.IAMPORT_SECRET
            }

            token_url = "https://api.iamport.kr/users/getToken"
            req = requests.post(token_url, data=token_access_data)
            token_access_res = req.json()
            access_token = token_access_res['response']['access_token']

            headers = {
                'Authorization': access_token
            }
            if models.Payment.objects.get(merchant_uid=item_merchant_uid).status == "cancelled":
                return Http404

            pay_imp_uid = models.Payment.objects.get(
                merchant_uid=item_merchant_uid).bucket_paid
            bucket_payment = models.BucketPayment.objects.get(
                imp_uid=pay_imp_uid
            )
            cancelled_payment = models.Payment.objects.filter(
                bucket_paid=bucket_payment)

            cancel_data = {
                'imp_uid': pay_imp_uid,
                'amount': request.POST.get("cancel_request_amount"),
            }

            cancel_url = "https://api.iamport.kr/payments/cancel/"
            cancel_req = requests.post(
                cancel_url, headers=headers, data=cancel_data)
            cancel_res = cancel_req.json()

            bucket_payment.paid_amount = int(
                bucket_payment.paid_amount) - int(request.POST.get("cancel_request_amount"))
            bucket_payment.save()

            for p in cancelled_payment:
                if int(p.merchant_uid) == int(item_merchant_uid):
                    p.status = "cancelled"
                    p.save()
                    item = items_models.Item.objects.get(pk=p.item.pk)
                    item.pay_count = int(item.pay_count) - int(p.item_count)
                    item.save()

            context = {
                'code': cancel_res['code'],
                'merchant_uid': cancel_res['response']['merchant_uid'],
                'pay_method': cancel_res['response']['pay_method'],
                'amount': cancel_res['response']['amount'],
                'status': cancel_res['response']['status'],
            }

            data = context

            return JsonResponse(data)


class AskingCancelView(LoggedInOnlyView, View):
    def get(self, request, *args, **kwargs):
        merchant_uid = kwargs.get("merchant_uid")
        if models.Payment.objects.filter(merchant_uid=merchant_uid):
            payment = models.Payment.objects.get(merchant_uid=merchant_uid)
        elif models.BucketPayment.objects.filter(merchant_uid=merchant_uid):
            payment = models.BucketPayment.objects.get(
                merchant_uid=merchant_uid)
        else:
            return Http404
        context = {'payment': payment}
        return render(request, 'payment/asking_cancel.html', context)
