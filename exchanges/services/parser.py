from .exchange_manager import ExchangeManager
from ..models import Exchange
from main.models import CoinPair


def main():
    ex = ExchangeManager()
    for coin_pair in CoinPair.objects.all():
        for exchange in Exchange.objects.all():
            #TODO create multithread and thread manager
            if ex.run_parse(coin_pair=coin_pair, exchange=exchange):
                print(True)
            else:
                print(False)
