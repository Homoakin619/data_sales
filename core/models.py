from django.db import models
from django.conf import settings

from django_jsonfield_backport.models import JSONField
import random
import string
import json

def get_ref_id():
	strings = string.ascii_lowercase + string.digits
	result = ''
	for i in range(8):
		result += ''.join(random.choice(strings))
	return result

NETWORKS = (
		('AIR','AIRTEL'),
		('MTN','MTN'),
		('GLO','GLO'),
		('ETI','ETISALAT')
	)

DATA_QTY = (
		('1GB','1GB'),
		('2GB','2GB')
	)

class Merchant(models.Model):
	logo = models.ImageField(null=True,blank=True)
	title = models.CharField(max_length=10,null=True)
	data_price = JSONField()

	def __str__(self):
		return self.title

	def get_item_price(self):
		result = []
		items = json.loads(self.data_price)
		for item in items:
			x = (item,items[item])
			result.append(x)
		return result

class CardTransactions(models.Model):
	transaction_id = models.CharField(max_length=100,unique=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
	successful = models.BooleanField(default=False)
	amount = models.IntegerField(null=True)
	date = models.DateField(auto_now_add=True)
	time = models.TimeField(auto_now_add=True)


class Cart(models.Model):
	item = models.CharField(max_length=10)
	price = models.IntegerField()

class Card(models.Model):
	name = models.CharField(max_length=100)

class Transaction(models.Model):
	transaction_id = models.CharField(max_length=100,unique=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
	beneficiary = models.BigIntegerField()
	successful = models.BooleanField(default=False)
	merchant = models.CharField(max_length=10,null=True)
	item_qty = models.CharField(max_length=5,null=True)
	price = models.IntegerField(null=True)
	date = models.DateField(auto_now_add=True)

	def __str__(self):
		return self.transaction_id

class Customer(models.Model):
	image = models.ImageField(null=True,blank=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
	card = models.ForeignKey(Card,models.SET_NULL,blank=True,null=True)
	ref_id = models.CharField(max_length=50,unique=True)
	phone = models.BigIntegerField(unique=True)
	balance = models.FloatField(default=00.00)
	pin = models.IntegerField(blank=True,null=True)
	activation_key = models.CharField(null=True,blank=True,max_length=100)
	verified = models.BooleanField(default=False)
	

	def __str__(self):
		return self.user.username

	def save(self, *args, **kwargs):
		if not self.pk:
			self.ref_id = get_ref_id()
			return super(Customer,self).save(*args,**kwargs)
		return super(Customer,self).save(*args,**kwargs)

