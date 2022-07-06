from django.contrib import messages
from django.forms import ValidationError
from django.shortcuts import redirect, render,get_object_or_404
from django.views import generic
from django.contrib.auth import login,authenticate,logout
from django.http import HttpResponseRedirect,JsonResponse
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User



from .models import Customer,Merchant,Cart, Transaction
from .forms import CustomerForm,CustomerDetailsForm, LoginForm, MerchantForm, PinForm

import stripe
import random
import string

def get_ref_id():
	strings = string.ascii_lowercase + string.digits
	result = ''
	for i in range(8):
		result += ''.join(random.choice(strings))
	return result

stripe.api_key = settings.STRIPE_KEY

def get_price(network,value):
    airtel ={'1GB':400,'2GB':750}
    mtn ={'1GB':400,'2GB':750}
    glo ={'1GB':350,'2GB':750}
    etisalat ={'1GB':350,'2GB':750}
    if network.lower() == 'airtel':
        return airtel[value]
    if network.lower() == 'mtn':
        return mtn[value]
    if network.lower() == 'glo':
        return glo[value]
    if network.lower() == 'etisalat':
        return etisalat[value]



class EditProfileView(generic.View):
    template_name = 'core/edit-profile.html'
    def get(self,*args,**kwargs):
        
        query = get_object_or_404(Customer,user=self.request.user)
        context = {}
        context['form'] = CustomerDetailsForm(instance=query)
        return render(self.request,self.template_name,context=context)
    def post(self,*args,**kwargs):
        query = get_object_or_404(Customer,user=self.request.user)
        form = CustomerDetailsForm(self.request.POST,instance=query)
        if form.is_valid():
            self.request.user.save()
            form.save()
            print('Form Passed')
            return HttpResponseRedirect(reverse('profile'))
        print('form failed')
        return self.get(*args,**kwargs)

class ProfileView(generic.View):
    template_name = 'core/profile.html'
    def get(self,*args,**kwargs):
        form = PinForm()
        context = {'form':form}
        context['customer'] = Customer.objects.get(user=self.request.user)
        return render(self.request,self.template_name,context=context)
    
    def post(self,*args,**kwargs):
        customer = Customer.objects.get(user=self.request.user)
        form = PinForm(self.request.POST)
        context = {'form':form}
        context['customer'] = Customer.objects.get(user=self.request.user)

        if form.is_valid():
            email = form.cleaned_data['email']
            pin = form.cleaned_data['pin']
            if email == self.request.user.email:
                customer.pin = pin
                customer.save()
                return self.get(*args,**kwargs)
            else:
                context['error'] = True
                return render(self.request,self.template_name,context=context)
        else:
            context['error'] = True
            return render(self.request,self.template_name,context=context)
        
        return render(self.request,self.template_name,context=context)
        

class DashboardView(generic.View):
    template_name = 'core/dash.html'
    def get(self,*args,**kwargs):
        context ={}
        context['stripe'] = settings.STRIPE_PK
        context['items']=Merchant.objects.all()
        return render(self.request,self.template_name,context=context)

    # post-method to purchase data
    def post(self,*args,**kwargs):
        user = self.request.user
        customer = get_object_or_404(Customer,user=user)

        if self.request.POST.get('form-name') == 'pin-form':
            merchant = self.request.POST.get('merchant')
            item_qty = self.request.POST.get('quantity')
            amount =  int(self.request.POST['amounts'])
            user_pin = customer.pin
            pin = self.request.POST.get('pin')
            recharge_self = self.request.POST.get('self_recharge',False)
            print(recharge_self)
            if not pin:
                messages.warning(self.request,'Pin cannot be blank')
                print('no pin')
            else:
                if int(pin) == user_pin:
                    if recharge_self is not False:
                        print('using default')
                        beneficiary = customer.phone
                    else:
                        print('picking beneficiary')
                        beneficiary = self.request.POST.get('beneficiary')
                    print(beneficiary)
                    
                    if not beneficiary:
                        print('no beneficiary')
                        messages.warning(self.request,'Kindly select a beneficiary to recharge, or tick checkbox to recharg for self!') 
                    
                    else:
                        print('saving data')
                        balance = customer.balance - amount
                        customer.balance = balance
                        customer.save()
                        transaction_id = get_ref_id()
                        price = get_price(merchant,item_qty)
                        transaction =Transaction.objects.create(
                                transaction_id=transaction_id, user=user, merchant=merchant, beneficiary=beneficiary, item_qty=item_qty, 
                                successful=True,price=price
                            )
                        transaction.save()
                        return HttpResponseRedirect(reverse('success'))
        return self.get(*args,**kwargs)
        
        
        # try:
        #     charge = stripe.Charge.create(
        #         amount=int(amount)*100,
        #         currency='usd',
        #         description='Example charged card',
        #         source=token,
        #         )

        # except stripe.error.CardError as e:
        # # Since it's a decline, stripe.error.CardError will be caught
        #     print('Status is: %s' % e.http_status)
        #     print('Code is: %s' % e.code)
        #     # param is '' in this case
        #     print('Param is: %s' % e.param)
        #     print('Message is: %s' % e.user_message)
        #     raise ValidationError(e)
        # except stripe.error.RateLimitError as e:
        # # Too many requests made to the API too quickly
        #     raise ValidationError(e)
        # except stripe.error.InvalidRequestError as e:
        # # Invalid parameters were supplied to Stripe's API
        #     raise ValidationError("there is an error at %s" %e.param)
        # except stripe.error.AuthenticationError as e:
        # # Authentication with Stripe's API failed
        # # (maybe you changed API keys recently)
        #     print("Message is: Authentication with Stripe's API failed")
        # except stripe.error.APIConnectionError as e:
        # # Network communication with Stripe failed
        #     print(e)
        #     raise ValidationError(e)
        # except stripe.error.StripeError as e:
        # # Display a very generic error to the user, and maybe send
        # # yourself an email
        # #     messages.error(self.request,'Your PIN is incorrect!')
        #     raise ValidationError(e)
        # except Exception as e:
        # # Something else happened, completely unrelated to Stripe
        #     raise ValidationError(e)
        # print(charge.id)
        # customer = get_object_or_404(User,username=self.request.user.username)
        # transaction = Transaction.objects.create(transaction_id=charge.id)
        # customer.transa

        


class TransactionView(generic.View):
    template_name = 'core/payment.html'
    def get(self,request,*args,**kwargs):
        intent = stripe.PaymentIntent.create(
            amount=1099,
            currency='usd',
            # Verify your integration in this guide by including this parameter
            metadata={'integration_check': 'accept_a_payment'},
            )
        context = {'client_secret':intent.client_secret }

        return render(self.request,self.template_name)

    def post(self,request,*args,**kwargs):
        amount =  request.POST.get('amount')
        token = request.POST.get('stripeToken')
        print(token)
        print(amount)
        try:
            charge = stripe.Charge.create(
                amount=amount*1000,
                currency='usd',
                description='Example charged card',
                source=token,
                )

        except stripe.error.CardError as e:
        # Since it's a decline, stripe.error.CardError will be caught
            print('Status is: %s' % e.http_status)
            print('Code is: %s' % e.code)
            # param is '' in this case
            print('Param is: %s' % e.param)
            print('Message is: %s' % e.user_message)
        except stripe.error.RateLimitError as e:
        # Too many requests made to the API too quickly
            pass
        except stripe.error.InvalidRequestError as e:
        # Invalid parameters were supplied to Stripe's API
            pass
        except stripe.error.AuthenticationError as e:
        # Authentication with Stripe's API failed
        # (maybe you changed API keys recently)
            print("Message is: Authentication with Stripe's API failed")
        except stripe.error.APIConnectionError as e:
        # Network communication with Stripe failed
            print(e)
        except stripe.error.StripeError as e:
        # Display a very generic error to the user, and maybe send
        # yourself an email
            pass

        except Exception as e:
        # Something else happened, completely unrelated to Stripe
            print(e)
        return HttpResponseRedirect(reverse('success'))
        
def success(request):
    return render(request,'core/success.html',{'message':'Transaction successful You will be credited soon!'})



def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')

class TransactionHistoryView(generic.View):
    template_name = 'core/transaction.html'
    def get(self,*args,**kwargs):
        transactions = Transaction.objects.filter(user=self.request.user).order_by('-id')
        print(transactions)
        context = {'transactions':enumerate(transactions,start=1)}
        return render(self.request,self.template_name,context=context)



class AdminHomepage(generic.View):
    template_name = 'core/admins/homepage.html'
    def get(self,*args,**kwargs):

        return render(self.request,self.template_name)

class AdminTransactions(generic.View):
    template_name = 'core/admins/transactions.html'
    def get(self,*args,**kwargs):
        context = {'transactions':enumerate(Transaction.objects.all().order_by('-id'),start=1)}
        return render(self.request,self.template_name,context=context)

class AdminListUsers(generic.ListView):
    template_name = 'core/admins/users.html'
    model = User
    context_object_name = 'customers'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        return context

class AdminListMerchants(generic.ListView):
    model = Merchant
    template_name = 'core/admins/merchants.html'
    context_object_name = 'merchants'
    
class AdminEditMerchant(generic.View):
    template_name = 'core/admins/edit_merchant.html'

    def get(self,*args, **kwargs):
        query = get_object_or_404(Merchant,id=self.kwargs['id'])
        form = MerchantForm(instance=query)
        context = {'form':form }
        return render(self.request,self.template_name,context=context)

    def post(self,*args,**kwargs):
        query = get_object_or_404(Merchant,id=self.kwargs['id'])
        form = MerchantForm(self.request.POST,instance=query)
        context = {'form':form }
        if form.is_valid:
            form.save()
            return HttpResponseRedirect(reverse('merchants'))
        return render(self.request,self.template_name,context=context)

class IndexView(generic.View):
    template_name = 'core/login.html'
    def get(self,*args,**kwargs):
        if self.request.user.is_authenticated:
            if self.request.user.is_staff:
                return HttpResponseRedirect(reverse('admins'))
            else:
                return HttpResponseRedirect('dashboard')
        form = CustomerForm()
        login_form = LoginForm()
        context = {'form':form,'login_form':login_form,'disp':False}

        return render(self.request,self.template_name,context=context)
    
    def post(self,*args,**kwargs):
        form = CustomerForm(self.request.POST or None)
        login_form = LoginForm(self.request.POST or None)
        context = {'form':form,'login_form':login_form,'disp':False}

        login_f = self.request.POST.get('login')
        signup = self.request.POST.get('signup')

        print('signup',signup)
        print('login',login_f)

        if login_f:
            print('I am here')
            if login_form.is_valid():
                print('Valid Form')
                username = login_form.cleaned_data['username']
                password = login_form.cleaned_data['password']
                user = authenticate(self.request,username=username,password=password)
                if user is not None:
                    login(self.request,user)
                    if self.request.user.is_staff:
                        return HttpResponseRedirect(reverse('admins'))
                    else:
                        return HttpResponseRedirect(reverse('dashboard'))
                else:
                    print('useless User')
                    print(login_form.errors)
                    context['errors'] = login_form.errors
                    return render(self.request,self.template_name,context=context)
            else: 
                print('Error .......')
                print(login_form.errors.as_data())
                print(login_form.errors)
                # context['errors'] = login_form.errors
                return render(self.request,self.template_name,context=context)
        elif signup is not None:
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password1']
                phone = form.cleaned_data['phone']
                print('username',username)
                form.save()
                new_user = authenticate(username=username,password=password)  
                customer = Customer.objects.create(user=new_user,phone=phone)
                customer.save()
                login(self.request,new_user)
                return HttpResponseRedirect('dashboard')
            else:
                print(form.errors)
                return render(self.request,self.template_name,{'form':form,'disp':True,'errors':form.errors})
        print('I skipped all!')
        return render(self.request,self.template_name,context=context)


class RegisterView(generic.View):
    template_name = 'core/index.html'
    def get (self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect('dashboard')
        form = CustomerForm()
        context = {'form':form}
        return render(self.request,self.template_name,context=context)


    def post(self,*args,**kwargs):
        form = CustomerForm(self.request.POST)
        if form.is_valid():
            user = form.save()
            username = self.request.POST['username']
            password = self.request.POST['password1']
            phone = self.request.POST['phone']
            new_user = authenticate(username=username,password=password)
            Customer.objects.create(user=user,phone=phone)
            login(self.request,new_user)
            return HttpResponseRedirect('dashboard')
        return render(self.request,self.template_name,context={'form':form})

