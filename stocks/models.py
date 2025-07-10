from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Stocks(models.Model):
    ticker = models.CharField(max_length=10)
    name = models.CharField(max_length=300)
    description = models.CharField(max_length=5000)
    curr_price = models.FloatField()

    def __str__(self):
        return self.name

class UserInfo(models.Model) :
    user  =  models.OneToOneField(User , on_delete=models.CASCADE)
    phone_number =  models.CharField(max_length=15, blank=True, null=True)
    address  =  models.CharField(max_length=500, blank=True, null=True)
    pancard_number  =  models.CharField(max_length=30, blank=True, null=True)
    pancard_image = models.ImageField(upload_to='uploads/pancards/', blank=True, null=True)
    user_image = models.ImageField(upload_to='uploads/users/', blank=True, null=True)

class UserStock(models.Model) :
    stock = models.ForeignKey(Stocks, on_delete=models.CASCADE)
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    purchase_quantity = models.IntegerField()
    purchase_price = models.FloatField()
