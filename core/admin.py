from django.contrib import admin

from .models import Customer,Card,Merchant,Transaction,Cart

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
	list_display = ['ref_id','phone','balance']

	search_fields = ['ref_id','phone',]

admin.site.register(Card)
admin.site.register(Cart)
admin.site.register(Merchant)

@admin.register(Transaction)
class Transaction(admin.ModelAdmin):
	list_display = ['transaction_id','date','merchant','item_qty','successful']

	search_fields = ['transaction_id']
