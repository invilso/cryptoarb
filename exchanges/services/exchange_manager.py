

from exchanges.models import Exchange
from exchanges.services.base_exchange import BaseExchange
from main.models import CoinPair
from .kucoin import KuCoin
from .binance import Binance
from .huobi import Huobi



class ExchangeManager:
    def __init__(self):
        pass

    def run_parse(self, coin_pair: CoinPair, exchange: Exchange):
        if exchange in coin_pair.supported_exchanges.all():
            exchange_instance: BaseExchange = self._get_exchange_instance(exchange)
            coin_pair_str = exchange_instance.preprocess_coin_pair(
                coin_pair.base_coin, coin_pair.quote_coin
            )
            asks, bids = exchange_instance.get_order_books(coin_pair_str)
            processed_data = exchange_instance.process_data(bids, asks, coin_pair)
            exchange_instance.save_data(
                processed_data=processed_data, exchange=exchange, coin_pair=coin_pair
            )
            return True
        else:
            return False

    def _get_exchange_instance(self, exchange: Exchange):
        
        if exchange.name == "binance":
            return Binance(
                exchange.api_key, exchange.api_secret, exchange.api_passphrase
            )
        elif exchange.name == "kucoin":
            return KuCoin(
                exchange.api_key, exchange.api_secret, exchange.api_passphrase
            )
        elif exchange.name == "huobi":
            return Huobi(exchange.api_key, exchange.api_secret, exchange.api_passphrase)