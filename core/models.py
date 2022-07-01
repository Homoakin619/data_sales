from django.db import models
from django.conf import settings

import jsonfield
import random
import string

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

class Item(models.Model):
	logo = models.ImageField(null=True,blank=True)
	title = models.CharField(max_length=10,null=True)
	data_price = jsonfield.JSONField()

	def __str__(self):
		return self.title

	def get_item_price(self):
		result = []
		items = self.data_price
		for item in items:
			x = (item,items[item])
			result.append(x)
		return result

class Cart(models.Model):
	item = models.CharField(max_length=10)
	price = models.IntegerField()

class Card(models.Model):
	name = models.CharField(max_length=100)

class Transaction(models.Model):
	transaction_id = models.CharField(max_length=100,unique=True)
	successful = models.BooleanField(default=False)
	item = models.ForeignKey(Item,on_delete=models.CASCADE,null=True)
	item_qty = models.IntegerField(null=True)
	date = models.DateField()

class Customer(models.Model):
	image = models.ImageField(null=True,blank=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
	card = models.ForeignKey(Card,models.SET_NULL,blank=True,null=True)
	ref_id = models.CharField(max_length=50,unique=True)
	phone = models.IntegerField(unique=True)
	balance = models.FloatField(default=00.00)
	pin = models.IntegerField(blank=True,null=True)
	transactions = models.ForeignKey(Transaction,models.SET_NULL,blank=True,null=True)

	def __str__(self):
		return self.user.username

	def save(self, *args, **kwargs):
		if not self.pk:
			self.ref_id = get_ref_id()
			return super(Customer,self).save(*args,**kwargs)
		return super(Customer,self).save(*args,**kwargs)

