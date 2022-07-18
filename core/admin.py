from django.contrib import admin
from django.contrib.admin.apps import AdminConfig
from django.contrib.admin.sites import AdminSite
from django.contrib.admin import options

from .models import Customer,Card,Merchant,Transaction,CardTransactions




class MyAdmin(AdminSite):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
	subtitle = ''
	site_header = 'Zeedah Data Admin'
	site_title = 'Zeedah Data Admin'
	index_title = 'Zeedah Data Administration'

	def has_permission(self, request):
		return request.user.is_superuser and request.user.is_active

	def each_context(self, request):
		context = super().each_context(request)
		context['subtitle'] = self.subtitle
		context['site_header'] = self.site_header
		return context
	
admin_site = MyAdmin()


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





# @admin.register(Customer)
# class CustomerAdmin(admin.ModelAdmin):
# 	list_display = ['ref_id','phone','balance']

# 	search_fields = ['ref_id','phone',]

# admin.site.register(Card,site=admin_site)
# # admin.site.register(Cart)
# admin.site.register(Merchant,site=admin_site)

# @admin.register(Transaction,site=admin_site)
# class Transaction(admin.ModelAdmin):
# 	list_display = ['transaction_id','date','merchant','item_qty','successful']

# 	search_fields = ['transaction_id']

# @admin.register(CardTransactions,site=admin_site)
# class CardTransactionAdmin(admin.ModelAdmin):
# 	list_display = ['user','transaction_id','date','amount','successful']
	
# 	search_fields = ['transation_id','date']
