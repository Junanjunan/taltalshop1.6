import os
import requests
import uuid
import math
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic import FormView, View, ListView
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from validate_email import validate_email
from . import forms, models
from items import models as items_models
from payments import models as payments_models
from .jusoConfmKey import jusoConfmKey
from config.local_settings import DEPLOY_URL, GH_ID_DEPLOY, GH_SECRET_DEPLOY, KAKAO_ID_DEPLOY, NAVER_ID_DEPLOY, NAVER_SECRET_DEPLOY, GH_ID_LOCAL, GH_SECRET_LOCAL, KAKAO_ID_LOCAL, NAVER_ID_LOCAL, NAVER_SECRET_LOCAL


class LoggedOutOnlyView(UserPassesTestMixin, View):
    def test_func(self):
        return not self.request.user.is_authenticated


class LoggedInOnlyView(LoginRequiredMixin):
    login_url = reverse_lazy('users:login')


class SignUpView(LoggedOutOnlyView, FormView):
    template_name = 'users/signup.html'
    form_class = forms.SignUpForm
    success_url = reverse_lazy('users:signup-after')

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=email, password=password)
        user.verify_email()
        return super().form_valid(form)


class SignUpAfterView(LoggedOutOnlyView, FormView):
    template_name = 'users/signup_after.html'
    form_class = forms.SignUpForm


def complete_verification(request, key):
    try:
        user = models.User.objects.get(email_secret=key)
        user.email_verified = True
        user.email_secret = ""
        user.save()
    except models.User.DoesNotExist:
        pass
    return redirect(reverse("users:login"))


class LoginView(LoggedOutOnlyView, FormView):
    template_name = 'users/login.html'
    form_class = forms.LoginForm
    success_url = reverse_lazy('home:home')

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=email, password=password)
        user_model = models.User.objects.get(username=email)
        login(self.request, user)
        return super().form_valid(form)


def log_out(request):
    logout(request)
    print(requests.__version__)
    return redirect(reverse("home:home"))


class UserStatusView(LoggedInOnlyView, ListView):
    model = models.User
    template_name = "users/status.html"

    def get_object(self, queryset=None):
        user = super().get_object(queryset=queryset)
        if user.realtor.pk != self.request.user.pk:
            raise Http404()
        return user


class UpdatePasswordView(LoggedInOnlyView, PasswordChangeView):
    form_class = forms.UpdatePasswordForm
    template_name = "users/update-password.html"

    def get_success_url(self):
        return self.request.user.get_absolute_url()


class ChangeUserInformationView(LoggedInOnlyView, View):
    def get(self, request, *args, **kwargs):
        user_pk = kwargs.get("pk")
        user = models.User.objects.get(pk=user_pk)
        
        phone_number = request.GET.get("phone_number")
        delivery_requirement = request.GET.get("delivery_requirement")
        address = request.GET.get("address")
        if phone_number:
            user.phone_number = phone_number
        if delivery_requirement:
            user.delivery_requirement = delivery_requirement
        if address:
            user.address = address
            user.address_detail = ""
        user.save()
        form = forms.UserInformationForm(instance=user)
        context = {
            'form': form,
        }
        return render(request, 'users/change_user_information.html', context)
    
    def post(self, request, *args, **kwargs):
        user_pk = kwargs.get("pk")
        user = models.User.objects.get(pk=user_pk)
        phone_number = request.POST.get("phone_number")
        delivery_requirement = request.POST.get("delivery_requirement")
        address = request.POST.get("address")
        address_detail = request.POST.get("address_detail")
        user.phone_number = phone_number
        user.delivery_requirement = delivery_requirement
        user.address = address
        user.address_detail = address_detail
        user.save()
        return redirect(reverse("users:status", kwargs={"pk": user.pk}))


class ChangeAddressView(LoggedInOnlyView, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'users/change_address.html')

    def post(self, request, *args, **kwargs):
        user_pk = kwargs.get("pk")
        url = 'https://www.juso.go.kr/addrlink/addrLinkApi.do'
        keyword = request.POST.get("keyword")
        countPerPage = 10
        page = int(request.POST.get("page"))
        data = {
            'confmKey': jusoConfmKey,
            'countPerPage': countPerPage,
            'currentPage': page,
            'keyword': keyword,
            'resultType': 'json'
        }

        req = requests.get(url, params=data)
        res = req.json()
        totalCount = res['results']['common']['totalCount']
        addrList = res['results']['juso']
        totalPage = math.ceil(int(totalCount)/countPerPage)

        context = {
            'data': data,
            'totalCount': totalCount,
            'addrList': addrList,
            'currentPage': page,
            'totalPage': range(0, totalPage),
            'totalPageNumber': totalPage
        }

        return render(request, 'users/change_address.html', context)

class ChangeAddressPaymentCreatingView(LoggedInOnlyView, View):
    def get(self, request, *args, **kwargs):
        receiver = request.GET['receiver']
        addressDetail = request.GET['addressDetail']
        phoneNumber = request.GET['phoneNumber']
        deliveryRequirement = request.GET['deliveryRequirement']
        context = {
            'receiver': receiver,
            'addressDetail': addressDetail,
            'phoneNumber': phoneNumber,
            'deliveryRequirement': deliveryRequirement,
        }
        return render(request, 'users/change_address_payment_creating.html', context)

    def post(self, request, *args, **kwargs):
        url = 'https://www.juso.go.kr/addrlink/addrLinkApi.do'
        keyword = request.POST.get("keyword")
        countPerPage = 10
        page = int(request.POST.get("page"))
        data = {
            'confmKey': jusoConfmKey,
            'countPerPage': countPerPage,
            'currentPage': page,
            'keyword': keyword,
            'resultType': 'json'
        }

        req = requests.get(url, params=data)
        res = req.json()
        totalCount = res['results']['common']['totalCount']
        addrList = res['results']['juso']
        totalPage = math.ceil(int(totalCount)/countPerPage)

        context = {
            'data': data,
            'totalCount': totalCount,
            'addrList': addrList,
            'currentPage': page,
            'totalPage': range(0, totalPage),
            'totalPageNumber': totalPage,
            'receiver': request.POST.get("receiver"),
            'addressDetail': request.POST.get("addressDetail"),
            'phoneNumber': request.POST.get("phoneNumber"),
            'deliveryRequirement': request.POST.get("deliveryRequirement"),
        }
        return render(request, 'users/change_address_payment_creating.html', context)


class ChangeAddressPaymentUpdatingView(LoggedInOnlyView, View):
    def get(self, request, *args, **kwargs):
        receiver = request.GET['receiver']
        addressDetail = request.GET['addressDetail']
        phoneNumber = request.GET['phoneNumber']
        deliveryRequirement = request.GET['deliveryRequirement']
        context = {
            'receiver': receiver,
            'addressDetail': addressDetail,
            'phoneNumber': phoneNumber,
            'deliveryRequirement': deliveryRequirement,
        }
        return render(request, 'users/change_address_payment_updating.html', context)

    def post(self, request, *args, **kwargs):
        url = 'https://www.juso.go.kr/addrlink/addrLinkApi.do'
        keyword = request.POST.get("keyword")
        countPerPage = 10
        page = int(request.POST.get("page"))
        data = {
            'confmKey': jusoConfmKey,
            'countPerPage': countPerPage,
            'currentPage': page,
            'keyword': keyword,
            'resultType': 'json'
        }

        req = requests.get(url, params=data)
        res = req.json()
        totalCount = res['results']['common']['totalCount']
        addrList = res['results']['juso']
        totalPage = math.ceil(int(totalCount)/countPerPage)

        context = {
            'data': data,
            'totalCount': totalCount,
            'addrList': addrList,
            'currentPage': page,
            'totalPage': range(0, totalPage),
            'totalPageNumber': totalPage,
            'receiver': request.POST.get("receiver"),
            'addressDetail': request.POST.get("addressDetail"),
            'phoneNumber': request.POST.get("phoneNumber"),
            'deliveryRequirement': request.POST.get("deliveryRequirement"),
        }
        return render(request, 'users/change_address_payment_updating.html', context)

class ItemSellerRequestView(LoggedInOnlyView, View):
    def get(self, request, pk):
        user = models.User.objects.get(pk=pk)
        print(user)
        user.item_seller_request = True
        user.save()
        return redirect('home:home')

"""회원탈퇴: https://parkhyeonchae.github.io/2020/03/31/django-project-15/"""


@login_required
def delete_another_address_payment(request, pk):
    print(pk)
    models.AnotherAddress.objects.get(pk=pk).delete()
    return redirect(reverse("payments:select-address", kwargs={"pk": request.user.pk}))


@login_required
def user_del(request):
    if request.method == 'POST':
        password_form = forms.CheckPasswordForm(request.user, request.POST)

        if password_form.is_valid():
            request.user.delete()
            logout(request)
            messages.success(request, "회원탈퇴가 완료되었습니다.")
            return redirect('home:home')
    else:
        password_form = forms.CheckPasswordForm(request.user)

    return render(request, 'users/user_del.html', {'password_form': password_form})


class RequestPasswordResetEmail(LoggedOutOnlyView, View):
    def get(self, request):
        return render(request, 'users/reset-password.html')

    def post(self, request):
        email = request.POST['email']
        context = {'values': request.POST}
        if not validate_email(email):
            messages.error(request, "올바른 이메일을 입력해주세요")
            return render(request, 'users/reset-password.html', context)

        current_site = get_current_site(request)
        user = models.User.objects.filter(email=email)

        if user.exists():
            if user[0].login_method == 'email':
                email_contents = {
                    'user': user[0],
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                    'token': PasswordResetTokenGenerator().make_token(user[0]),
                }
                link = reverse('users:reset-user-password', kwargs={
                               'uidb64': email_contents['uid'], 'token': email_contents['token']})
                email_subject = '탈탈샵 비밀번호 재설정 이메일입니다'
                reset_url = 'http://' + current_site.domain + link
                html_message = render_to_string(
                    "emails/password_reset_email.html", {
                        "reset_url": reset_url}
                )
                send_mail(
                    email_subject,
                    strip_tags(html_message),
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                    html_message=html_message,
                )

            else:
                messages.error(request, "비밀번호를 바꿀 수 없는 아이디입니다.")
                return render(request, 'users/reset-password.html', context)
        else:
            messages.error(request, "가입되지 않은 이메일입니다.")
            return redirect("users:request-password")
        return render(request, 'users/sending-password-email-done.html')


class CompletePasswordReset(LoggedOutOnlyView, View):

    def get(self, request, uidb64, token):
        context = {'uidb64': uidb64, 'token': token}
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = models.User.objects.get(pk=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(request, '새로운 인증메일 링크를 이용해주세요')
                return render(request, 'users/reset-password.html')
        except:
            pass
        return render(request, 'users/set-new-password.html', context)

    def post(self, request, uidb64, token):
        context = {'uidb64': uidb64, 'token': token}
        password = request.POST['password']
        password1 = request.POST['password1']
        if password != password1:
            messages.error(request, '비밀번호가 일치하지 않습니다')
            return render(request, 'users/set-new-password.html', context)
        if len(password) < 6:
            messages.error(request, '6 글자 이상으로 설정해주세요')
            return render(request, 'users/set-new-password.html', context)
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = models.User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(request, '비밀번호가 정상적으로 바뀌었습니다')
            return redirect('users:login')
        except:
            messages.info(request, 'Somethin went wrong')
            return render(request, 'users/set-new-password.html', context)


class SendingPasswordEmailDone(LoggedOutOnlyView, View):
    template_name = "users/sending-email-done.html"


def github_login(request):
    if settings.DEBUG == True:
        client_id = GH_ID_LOCAL
        redirect_uri = "http://127.0.0.1:8000/users/login/github/callback/"
    else:
        client_id = GH_ID_DEPLOY
        redirect_uri = f"{DEPLOY_URL}/users/login/github/callback/"
    return redirect(f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=read:user")


def github_callback(request):
    if settings.DEBUG == True:
        client_id = GH_ID_LOCAL
        client_secret = GH_SECRET_LOCAL
    else:
        client_id = GH_ID_DEPLOY
        client_secret = GH_SECRET_DEPLOY
    code = request.GET.get("code")
    result = requests.post(
        f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}",
        headers={"Accept": "application/json"},)
    result_json = result.json()
    access_token = result_json.get("access_token")
    profile_request = requests.get(
        "https://api.github.com/user",
        headers={
            "Authorization": f"token {access_token}",
            "Accept": "application/json"})
    profile_json = profile_request.json()
    email = profile_json.get("email")
    first_name = profile_json.get("name")
    try:
        user = models.User.objects.get(username=email)
        if user.login_method != models.User.LOGIN_GITHUB:
            messages.error(request, "다른 경로로 가입되어있는 이메일입니다")
            return redirect("users:login")
    except models.User.DoesNotExist:
        user = models.User.objects.create(
            username=email,
            email=email,
            first_name=first_name,
            login_method=models.User.LOGIN_GITHUB
        )
        user.set_unusable_password()
        user.email_verified = True
        user.save()
    login(request, user)
    return redirect(reverse("home:home"))


def kakao_login(request):
    if settings.DEBUG == True:
        REST_API_KEY = KAKAO_ID_LOCAL
        REDIRECT_URI = "http://127.0.0.1:8000/users/login/kakao/callback/"
    else:
        REST_API_KEY = KAKAO_ID_DEPLOY
        REDIRECT_URI = f"{DEPLOY_URL}/users/login/kakao/callback/"
    return redirect(f"https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}&response_type=code")


class KakaoException(Exception):
    pass


def kakao_callback(request):
    try:
        if settings.DEBUG == True:
            REST_API_KEY = KAKAO_ID_LOCAL
            REDIRECT_URI = "http://127.0.0.1:8000/users/login/kakao/callback/"
        else:
            REST_API_KEY = KAKAO_ID_DEPLOY
            REDIRECT_URI = f"{DEPLOY_URL}/users/login/kakao/callback/"
        code = request.GET.get("code")
        token_request = requests.get(
            f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={REST_API_KEY}&redirect_uri={REDIRECT_URI}&code={code}")
        token_json = token_request.json()
        access_token = token_json.get("access_token")
        profile_request = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={
                "Authorization": f"Bearer {access_token}", })
        profile_json = profile_request.json()
        # properties = profile_json.get("properties")
        # kakao_id = profile_json.get("id")
        kakao_account = profile_json.get("kakao_account")
        email = kakao_account.get("email")
        if email is None:
            messages.error(request, "이메일 이용에 동의하지 않으셨습니다.")
            return redirect("users:login")
        # nickname = properties.get("nickname")
        # profile_image = properties.get("profile_image")
        try:
            user = models.User.objects.get(username=email)
            if user.login_method != models.User.LOGIN_KAKAO:
                messages.error(request, "다른 경로로 가입되어있는 이메일입니다")
                return redirect("users:login")
        except models.User.DoesNotExist:
            user = models.User.objects.create(
                email=email,
                username=email,
                # first_name=nickname,
                login_method=models.User.LOGIN_KAKAO,
            )
            user.set_unusable_password()
            user.email_verified = True
            user.save()
            # if profile_image is not None:
            #     photo_request = requests.get(profile_image)
            #     user.avatar.save(f"{nickname}-avatar",
            #                      ContentFile(photo_request.content))
        login(request, user)
        return redirect(reverse("home:home"))
    except KakaoException:
        return redirect(reverse("users:login"))


def naver_login(request):
    if settings.DEBUG == True:
        client_id = NAVER_ID_LOCAL
        redirect_uri = "http://127.0.0.1:8000/users/login/naver/callback/"
    else:
        client_id = NAVER_ID_DEPLOY
        redirect_uri = f"{DEPLOY_URL}/users/login/naver/callback/"
    state = uuid.uuid4().hex[:20]
    return redirect(f"https://nid.naver.com/oauth2.0/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&state={state}")


def naver_callback(request):
    if settings.DEBUG == True:
        client_id = NAVER_ID_LOCAL
        client_secret = NAVER_SECRET_LOCAL
    else:
        client_id = NAVER_ID_DEPLOY
        client_secret = NAVER_SECRET_DEPLOY
    code = request.GET.get("code")
    state = request.GET.get("state")
    token_request = requests.post(
        f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id={client_id}&client_secret={client_secret}&code={code}&state={state}"
    )
    token_json = token_request.json()
    access_token = token_json.get("access_token")
    profile_request = requests.get(
        "https://openapi.naver.com/v1/nid/me",
        headers={
            "Authorization": f"Bearer {access_token}",
        }
    )
    profile_json = profile_request.json()
    response = profile_json.get("response")
    email = response.get("email")
    first_name = response.get("email")
    try:
        user = models.User.objects.get(username=email)
        if user.login_method != models.User.LOGIN_NAVER:
            messages.error(request, "다른 경로로 가입되어있는 이메일입니다")
            return redirect("users:login")
    except models.User.DoesNotExist:
        user = models.User.objects.create(
            email=email,
            username=email,
            first_name=first_name,
            login_method=models.User.LOGIN_NAVER
        )
        user.set_unusable_password()
        user.email_verified = True
        user.save()
    login(request, user)
    return redirect(reverse("home:home"))


class CustomerBucket(LoggedInOnlyView, View):
    def get(self, request, *args, **kwargs):
        user = models.User.objects.get(pk=request.user.pk)
        bucket_items = models.Bucket.objects.filter(user=user)
        item_amount = 0
        deli_fee_amount = 0
        for item in bucket_items:
            item_amount += int(item.total_price())
            deli_fee_amount += int(item.item.deli_fee)
        total_amount = item_amount + deli_fee_amount
        return render(
            request,
            'users/customer_bucket.html',
            {
                "user": user,
                'item_amount': item_amount,
                'deli_fee_amount': deli_fee_amount,
                'total_amount': total_amount
            }
        )


@login_required
def deleteBucket(request, pk, bucket_pk):
    models.Bucket.objects.filter(pk=bucket_pk).delete()
    return redirect(reverse("users:customer-bucket", kwargs={"pk": request.user.pk}))


@login_required
def changeBucket(request, pk):
    print(request)
    item_pk = request.POST.get("item_pk")
    item = items_models.Item.objects.get(pk=item_pk)
    item_count = request.POST.get("item_count")
    if models.Bucket.objects.filter(user=request.user, item=item):
        existed_bucket = models.Bucket.objects.get(
            user=request.user, item=item)
        existed_bucket.item_count = int(item_count)
        existed_bucket.save()
    else:
        models.Bucket.objects.create(
            user=request.user, item=item, item_count=item_count, deli_fee=item.deli_fee)
    return redirect(reverse("users:customer-bucket", kwargs={"pk": request.user.pk}))


class CustomerPaymentListView(LoggedInOnlyView, View):
    def get(self, request):
        payment_list = payments_models.Payment.objects.filter(user = request.user, status = "paid").order_by("-created")
        context = {
            'payment_list': payment_list,
        }
        return render(request, 'users/payment_list.html', context)


class CustomerPaymentCancellListView(LoggedInOnlyView, View):
    def get(self, request):
        cancelled_list = payments_models.Payment.objects.filter(user=request.user, status="cancelled").order_by("-created")
        context = {
            'cancelled_list': cancelled_list
        }
        return render(request, 'users/payment_cancell_list.html', context)


class CustomerFavsList(LoggedInOnlyView, View):
    def get(self, request):
        user = models.User.objects.get(pk=request.user.pk)
        favs = models.Fav.objects.filter(user=user)
        return render(request, 'users/favs_list.html', {'favs': favs})


class CustomerInquiryList(LoggedInOnlyView, View):
    def get(self, request):
        return render(request, 'users/inquiry_list.html')
    

class CreatingAnotherAddressView(LoggedInOnlyView, View):
    def get(self, request):
        context = {
            'receiver': request.GET.get("receiver"),
            'address': request.GET.get("roadAddr"),
            'addressDetail': request.GET.get("addressDetail"),
            'phoneNumber': request.GET.get("phoneNumber"),
            'deliveryRequirement': request.GET.get("deliveryRequirement"),
        }
        return render(request, 'users/creating_another_address.html', context)

    def post(self, request):
        receiver = request.POST.get("receiver")
        phone_number = request.POST.get("phone_number")
        address = request.POST.get("address")
        address_detail = request.POST.get("address_detail")
        delivery_requirement = request.POST.get("delivery_requirement")
        models.AnotherAddress.objects.create(
            user = request.user,
            receiver = receiver,
            phone_number = phone_number,
            address = address,
            address_detail = address_detail,
            delivery_requirement = delivery_requirement
        )
        return redirect(reverse("payments:select-address", kwargs={"pk": request.user.pk}))


class UpdatingAnotherAddressView(LoggedInOnlyView, View):
    def get(self, request, *args, **kwargs):
        another_address_pk = kwargs.get("pk")
        another_address = models.AnotherAddress.objects.get(pk = another_address_pk)
        context = {
            'another_address': another_address,
            'receiver': request.GET.get("receiver"),
            'address': request.GET.get("roadAddr"),
            'addressDetail': request.GET.get("addressDetail"),
            'phoneNumber': request.GET.get("phoneNumber"),
            'deliveryRequirement': request.GET.get("deliveryRequirement"),
        }
        return render(request, 'users/updating_another_address.html', context)

    def post(self, request, *args, **kwargs):
        another_address_pk = kwargs.get("pk")
        another_address = models.AnotherAddress.objects.get(pk = another_address_pk)
        receiver = request.POST.get("receiver")
        phone_number = request.POST.get("phone_number")
        address = request.POST.get("address")
        address_detail = request.POST.get("address_detail")
        delivery_requirement = request.POST.get("delivery_requirement")
        another_address.receiver = receiver
        another_address.phone_number = phone_number
        another_address.address = address
        another_address.address_detail = address_detail
        another_address.delivery_requirement = delivery_requirement
        another_address.save()
        return redirect(reverse("payments:select-address", kwargs={"pk": request.user.pk}))