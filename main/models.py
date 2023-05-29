from django.db import models
from exchanges.models import Exchange


# Create your models here.
class CoinPair(models.Model):
    base_coin = models.CharField(max_length=50)
    quote_coin = models.CharField(max_length=50)
    sell_net = models.CharField(max_length=5, null=True, blank=True)
    supported_exchanges = models.ManyToManyField(Exchange)

    def __str__(self):
        return f"{self.base_coin}/{self.quote_coin}"


class Order(models.Model):
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    coin_pair = models.ForeignKey(CoinPair, on_delete=models.CASCADE)
    price = models.FloatField()
    quantity = models.FloatField()
    quantity_usd = models.FloatField(null=True, blank=True)
    order_type = models.CharField(
        max_length=4, choices=(("ask", "Ask"), ("bid", "Bid"))
    )

    def __str__(self):
        return (
            f"{self.coin_pair} - {self.exchange}: Price: {self.price}, Quantity: {self.quantity}, Type: {self.order_type}, USD: {self.quantity_usd}"
        )
