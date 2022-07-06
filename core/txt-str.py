# class TransactionView(generic.View):
#     template_name = 'core/payment.html'
#     def get(self,request,*args,**kwargs):

#         return render(self.request,self.template_name)

#     def post(self,request,*args,**kwargs):
#         stripe.api_key = ''
#         intent = stripe.PaymentIntent.create(
#             amount=1099,
#             currency='usd',
#             # Verify your integration in this guide by including this parameter
#             metadata={'integration_check': 'accept_a_payment'},
#             )
#         context = {'client_secret':intent.client_secret }
#         return JsonResponse({'client_secret':intent.client_secret })

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