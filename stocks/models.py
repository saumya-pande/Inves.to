from django.db import models

# Create your models here.

class Stocks(models.Model):
    ticker = models.CharField(max_length=10)
    name = models.CharField(max_length=300)
    description = models.CharField(max_length=5000)
    curr_price = models.FloatField()

    def __str__(self):
        return self.ticker