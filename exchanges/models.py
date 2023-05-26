from django.db import models

# Create your models here.
class Exchange(models.Model):
    EXCHANGE_CHOICES = [
        ('binance', 'Binance'),
        ('kucoin', 'KuCoin'),
    ]

    name = models.CharField(max_length=50, choices=EXCHANGE_CHOICES)
    website = models.URLField()
    api_key = models.CharField(max_length=100, default="YOUR_API_KEY")
    api_secret = models.CharField(max_length=100, default="YOUR_API_SECRET")
    api_passphrase = models.CharField(max_length=100, default="YOUR_API_PASSPHRASE")
    sell_percentage = models.FloatField(default=0.5)
    buy_percentage = models.FloatField(default=0.5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name