from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from  django.core.exceptions import ValidationError
from django.contrib.auth.models import Group

from .models import Customer

class CustomerForm(UserCreationForm):
    username = forms.CharField(label='Username')
    email = forms.EmailField(label='Email')
    password1= forms.CharField(label='Password',widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password',widget=forms.PasswordInput)
    phone = forms.IntegerField(label='Phone',widget=forms.NumberInput)

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


class CustomerDetailsForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('phone',)

# class PaymentForm(forms.Form):
#     pay_user = forms.ChoiceField(label='self',widget=forms.CheckboxInput())