from django.contrib import admin
from django.contrib.admin.apps import AdminConfig

from django.contrib.admin import options

from .models import Customer,Card,Merchant,Transaction,CardTransactions




class MyAdmin(admin.AdminSite):
	subtitle = 'mysub'
	site_header = 'Zeedah Data Administration'
	# def each_context(self, request):
	# 	context = super().each_context(request)
	# 	context['subtitle'] = self.subtitle
	# 	context['site_header'] = self.site_header
	# 	return context
	
# admin_site = MyAdmin()

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
	list_display = ['ref_id','phone','balance']

	search_fields = ['ref_id','phone',]

admin.site.register(Card)
# admin.site.register(Cart)
admin.site.register(Merchant)

@admin.register(Transaction)
class Transaction(admin.ModelAdmin):
	list_display = ['transaction_id','date','merchant','item_qty','successful']

	search_fields = ['transaction_id']

@admin.register(CardTransactions)
class CardTransactionAdmin(admin.ModelAdmin):
	list_display = ['user','transaction_id','date','amount','successful']
	
	search_fields = ['transation_id','date']
