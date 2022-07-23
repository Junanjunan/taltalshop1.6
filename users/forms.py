from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import check_password
from . import models

class SampleException(Exception):
    pass

""" username check / error / """
"""https://stackoverflow.com/questions/20010108/checking-if-username-exists-in-django"""

class SignUpForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ('email',)
    
    email = forms.EmailField(label="", widget=forms.EmailInput(attrs={'placeholder':'아이디(이메일)', 'class':'login-form'}))
    password = forms.CharField(label="", widget=forms.PasswordInput(attrs={'placeholder':'비밀번호', 'class':'login-form'}))
    password1 = forms.CharField(label="", widget=forms.PasswordInput(attrs={'placeholder':'비밀번호 확인', 'class':'login-form'}))

    def clean_email(self):
        email = self.cleaned_data['email']
        if models.User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
        # 중간에 exclude(pk=self.instance.pk) 없어도 똑같이 기능하는 듯
            raise forms.ValidationError('해당 이메일의 유저가 이미 존재합니다.')
            # raise forms.ValidationError(u'해당 이메일("%s")의 유저가 이미 존재합니다.' % email)
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password')
        password1 = self.cleaned_data.get('password1')
        if password != password1:
            raise forms.ValidationError('비밀번호가 일치하지 않습니다')
        else:
            return password

    def save(self, *args, **kwargs):
        user = super().save(commit=False)
        email = self.cleaned_data.get('email')   
        password = self.cleaned_data.get('password')
        user.username = email
        user.set_password(password)
        user.save()
        
            
class LoginForm(forms.Form):
    email = forms.EmailField(label="", widget=forms.EmailInput(attrs={'placeholder':'아이디(이메일)', 'class':'login-form'}))
    password = forms.CharField(label="", widget=forms.PasswordInput(attrs={'placeholder':'비밀번호', 'class':'login-form'}))

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        try:
            user = models.User.objects.get(email=email)
            if user.email_verified:
                if user.check_password(password):
                    return self.cleaned_data
                else:
                    self.add_error("email", forms.ValidationError("이메일 또는 비밀번호를 다시 확인해주세요."))
            else:
                self.add_error("email", "인증 되지 않은 유저입니다. 이메일을 확인해주세요.")
        except models.User.DoesNotExist:
            self.add_error("email", forms.ValidationError("이메일 또는 비밀번호가 틀렸거나 존재하지 않는 유저입니다."))


class UpdatePasswordForm(PasswordChangeForm):
    old_password = forms.CharField( widget=forms.PasswordInput(attrs={'placeholder':'현재 비밀번호', 'class':'login-form'}))
    new_password1 = forms.CharField( widget=forms.PasswordInput(attrs={'placeholder':'새 비밀번호', 'class':'login-form'}))
    new_password2 = forms.CharField( widget=forms.PasswordInput(attrs={'placeholder':'새 비밀번호 확인', 'class':'login-form'}))

    class Meta:
        model = models.User
        fields = ('old_password', 'new_password1', 'new_password2')


"""회원탈퇴: https://parkhyeonchae.github.io/2020/03/31/django-project-15/"""
class CheckPasswordForm(forms.Form):
    password = forms.CharField(label='비밀번호', widget=forms.PasswordInput(
        attrs={'placeholder':'비밀번호', 'class': 'login-form',}), 
    )
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = self.user.password
        
        if password:
            if not check_password(password, confirm_password):
                self.add_error('password', '비밀번호가 일치하지 않습니다.')


class UserInformationForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = (
            'phone_number', 
            'address',
            'address_detail',
            'delivery_requirement'
            )
        widgets = {
                'address': forms.TextInput(attrs={'placeholder': '주소 검색하기', 'size': 100}),
                'address_detail': forms.TextInput(attrs={'placeholder': '상세주소', 'size': 100}),
                'delivery_requirement': forms.TextInput(attrs={'size': 100}),
            }