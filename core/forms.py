from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from  django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate

import json


from .models import Customer,Merchant

class LoginForm(forms.Form):
    username = forms.CharField(label='Username',widget=forms.TextInput(attrs={"class":"form-control", "id":"floatingInput", "placeholder":"username", "autofocus":True }))
    password = forms.CharField(label='Password',widget=forms.PasswordInput(attrs={"class":"form-control", "id":"floatingPassword", "placeholder":"Password"}))

    def clean_username(self):
        username = self.cleaned_data['username']
        if username is None:
            raise ValidationError('Username Cannot be empty')
        if len(username) < 3:
            raise ValidationError('Enter a valid username')
        query = User.objects.filter(username=username).exists()
        if not query:
            raise ValidationError('Username does not exist')
        return username
        

class CustomerForm(UserCreationForm):
    username = forms.CharField(label='Username',widget=forms.TextInput(attrs={"class":"form-control", "id":"floatingInput", "placeholder":"username", "autofocus":True }))
    email = forms.EmailField(label='Email',widget=forms.EmailInput(attrs={"class":"form-control", "id":"floatingInput", "placeholder":"name@example.com"}))
    password1= forms.CharField(label='Password',widget=forms.PasswordInput(attrs={"class":"form-control", "id":"floatingPassword", "placeholder":"Password"}))
    password2 = forms.CharField(label='Confirm Password',widget=forms.PasswordInput(attrs={"class":"form-control", "id":"floatingPassword1", "placeholder":"Confirm Password"}))
    phone = forms.IntegerField(label='Phone',widget=forms.NumberInput(attrs={"class":"form-control", "id":"floatingInput", "placeholder":"Phone"}))

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        new = User.objects.filter(username=username)
        if new.count():
            raise ValidationError('Username already taken!')
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        new = User.objects.filter(email=email)
        if new.count():
            raise ValidationError('Email Exists!')
        return email

    def clean_password2(self):
        password1= self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']

        if password1 and password2 and password1!= password2:
            raise ValidationError('Passwords do not match!')
        return password2

    def save(self, commit=True):
        user = User.objects.create_user(self.cleaned_data['username'],self.cleaned_data['email'],self.cleaned_data['password1'])
        user.is_staff = False
        group = Group.objects.get(name='customers')
        user.groups.add(group)
        return user

class MerchantForm(forms.ModelForm):
    logo = forms.FileField(widget=forms.ClearableFileInput())
    title = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    data_price = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}))

    def clean_data_price(self):
        data_price = self.cleaned_data['data_price']
        data_price =data_price.replace("'",'"')
        try:
            result = json.loads(data_price)
        except ValueError:
            raise ValueError('Syntax is invalid, Enter a valid syntax')
        return result
        
    class Meta:
        model = Merchant
        fields = '__all__'


class CustomerDetailsForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('phone',)

class ChangePinForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class":"form-control","id":"email_id"}))
    pin = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control',"id":"pin_id"}))

    def clean_pin(self):
        pin = str(self.cleaned_data['pin'])
        if len(pin) > 4 :
            raise ValidationError('Please enter a valid 4-digit PIN')
        try:
            pin = int(pin)
        except ValueError:
            raise ValidationError('PIN cannot be string, enter a valid number as PIN')
        return pin
        
class PinPurchaseForm(forms.Form):
    pin = forms.IntegerField(widget=forms.NumberInput(attrs={"type":"password", "class":"form-control","id":"pin","name":"pin","placeholder":"Enter PIN"}))
    beneficiary = forms.IntegerField(required=False,widget=forms.NumberInput(attrs={"class":"form-control","name":"beneficiary","placeholder":"Enter Beneficiary"}))
    amounts = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control'}))

    def clean_pin(self):
        pin = str(self.cleaned_data['pin'])
        if len(pin) < 4 or len(pin) > 4:
            raise ValidationError('Enter a valid 4-digit PIN')
        try:
            pin = int(pin)
        except ValueError:
            raise ValidationError('PIN cannot be a string')
        return pin

    # def clean_beneficiary(self):
    #     beneficiary = str(self.cleaned_data['beneficiary'])
    #     if len(beneficiary) > 10 or len(beneficiary) < 10:
    #         raise ValidationError('Enter a valid mobile number for beneficiary')
    #     try:
    #         beneficiary = int(beneficiary)
    #     except ValueError:
    #         raise ValidationError('Enter a valid mobile number for beneficiary')
    #     return beneficiary
        