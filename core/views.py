from msilib.schema import Error
from django.contrib import messages
from django.forms import ValidationError
from django.shortcuts import redirect, render
from django.views import generic
from django.contrib.auth import login,authenticate,logout
from django.http import HttpResponseRedirect,JsonResponse
from django.urls import reverse
from django.conf import settings



from .models import Customer,Item,Cart
from .forms import CustomerForm
import stripe

stripe.api_key = settings.STRIPE_KEY

def get_price(network,value):
    airtel ={'1GB':400,'2gb':750}
    mtn ={'1GB':400,'2gb':750}
    glo ={'1GB':350,'2gb':750}
    if network.lower() == 'airtel':
        print(airtel[value])
        return airtel[value]
    if network.lower() == 'mtn':
        print(mtn[value])
        return mtn[value]
    if network.lower() == 'glo':
        # print(glo[value])
        return glo[value]

class IndexView(generic.View):
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

class DashboardView(generic.View):
    template_name = 'core/dash.html'
    def get(self,*args,**kwargs):
        user = self.request.user
        context ={ }
        if user.is_authenticated:
            customer = Customer.objects.get(user=user)
            context['balance']=customer.balance
        context['stripe'] = settings.STRIPE_KEY
        context['items']=Item.objects.all()
        return render(self.request,self.template_name,context=context)

    # post-method to purchase data
    def post(self,*args,**kwargs):
        print(self.request)
        amount =  self.request.POST['amount']
        token = self.request.POST.get('stripeToken')
        print('Token: ',token)
        print('Amount: ',amount)
        try:
            charge = stripe.Charge.create(
                amount=int(amount)*100,
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
            raise ValidationError(e)
        except stripe.error.RateLimitError as e:
        # Too many requests made to the API too quickly
            raise ValidationError(e)
        except stripe.error.InvalidRequestError as e:
        # Invalid parameters were supplied to Stripe's API
            raise ValidationError("there is an error at %s" %e.param)
        except stripe.error.AuthenticationError as e:
        # Authentication with Stripe's API failed
        # (maybe you changed API keys recently)
            print("Message is: Authentication with Stripe's API failed")
        except stripe.error.APIConnectionError as e:
        # Network communication with Stripe failed
            print(e)
            raise ValidationError(e)
        except stripe.error.StripeError as e:
        # Display a very generic error to the user, and maybe send
        # yourself an email
            raise ValidationError(e)
        except Exception as e:
        # Something else happened, completely unrelated to Stripe
            raise ValidationError(e)
       
        return HttpResponseRedirect(reverse('success'))
        # pin = int(self.request.POST.get('pin'))
        # quantity = self.request.POST.get('price')
        # user = self.request.user
        # customer = Customer.objects.get(user=user)
        # customer_pin = customer.pin
        # balance = customer.balance
        # network = self.request.POST['network']
        # price = get_price(network,quantity)
        # print(price)
        # if pin == customer_pin:
        #     if price < balance:
        #         customer.balance = balance - price
        #         customer.save()
        #         messages.success(self.request,'Purchase succesful, you will be credited soon')
        #         return HttpResponseRedirect(reverse('success'))
        #     else:
        #         messages.error(self.request,'You do not have sufficient balance kindly credit your account')
        #         return HttpResponseRedirect(reverse('transact'))
        # else:
        #     messages.error(self.request,'Your PIN is incorrect!')
        # return self.get(*args,**kwargs)

        
        # if network:
        #     return HttpResponseRedirect(reverse('success'))
        # return self.get(*args,**kwargs)


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
        # if Cart.objects.all().count():
        #     Cart.objects.all().delete()
        # value = self.kwargs['value']
        # item = Item.objects.get(pk=self.kwargs['pk'])
        # title = item.title
        # price = get_price(item.title,value)
        # if price and title:
        #     Cart.objects.create(item=title,price=price)
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

def login_user(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request,username=username,password=password)
    if user is not None:
        login(request,user)
        # context = {'message':''}
        return HttpResponseRedirect(reverse('dashboard'))
    return render(request,'core/login.html')

def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')




# class TransactionView(generic.View):
#     template_name = 'core/payment.html'
#     def get(self,request,*args,**kwargs):

#         return render(self.request,self.template_name)

    # def post(self,request,*args,**kwargs):
    #     stripe.api_key = ''
    #     intent = stripe.PaymentIntent.create(
    #         amount=1099,
    #         currency='usd',
    #         # Verify your integration in this guide by including this parameter
    #         metadata={'integration_check': 'accept_a_payment'},
    #         )
    #     context = {'client_secret':intent.client_secret }
    #     return JsonResponse({'client_secret':intent.client_secret })

# def payment(request):
#     stripe.api_key = ''
#     intent = stripe.PaymentIntent.create(
#             amount=1099,
#             currency='usd',
#             # Verify your integration in this guide by including this parameter
#             metadata={'integration_check': 'accept_a_payment'},
#             )
#     context = {'client_secret':intent.client_secret }
#     return JsonResponse({'client_secret':intent.client_secret })