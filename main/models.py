from django.db import models
from exchanges.models import Exchange

# Create your models here.
class CoinPair(models.Model):
    base_coin = models.CharField(max_length=50)
    quote_coin = models.CharField(max_length=50)
    supported_exchanges = models.ManyToManyField(Exchange)

    def __str__(self):
        return f"{self.base_coin}/{self.quote_coin}"
    

class Order(models.Model):
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    coins = models.ForeignKey(CoinPair, on_delete=models.CASCADE)
    price = models.FloatField()
    quantity = models.FloatField()
    order_type = models.CharField(max_length=4, choices=(('sell', 'Sell'), ('buy', 'Buy')))

    def __str__(self):
        return f"Price: {self.price}, Quantity: {self.quantity}, Type: {self.order_type}"