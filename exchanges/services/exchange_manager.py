from exchanges.models import Exchange
from exchanges.services.base_exchange import BaseExchange
from main.models import CoinPair
from .kucoin import KuCoin
from .binance import Binance
from .huobi import Huobi
from .poloniex import Poloniex
from .ascendex import AscendEX
from .okx import OKX
from .bybit import ByBit


class ExchangeManager:
    def __init__(self):
        pass
    #TODO refactor this
    def run_parse(self, coin_pair: CoinPair, exchange: Exchange, proxies: dict[str, str]):
        if exchange in coin_pair.supported_exchanges.all():
            exchange_instance: BaseExchange = self._get_exchange_instance(exchange)
            exchange_instance.set_proxy(proxies)
            coin_pair_str = exchange_instance.preprocess_coin_pair(
                coin_pair.base_coin, coin_pair.quote_coin
            )
            asks, bids = exchange_instance.get_order_books(coin_pair_str)
            processed_data = exchange_instance.process_data(bids, asks, coin_pair)
            processed_data = exchange_instance.apply_commission(processed_data, exchange)
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

        elif exchange.name == "poloniex":
            return Poloniex(
                exchange.api_key, exchange.api_secret, exchange.api_passphrase
            )

        elif exchange.name == "bybit":
            return ByBit(exchange.api_key, exchange.api_secret, exchange.api_passphrase)
        elif exchange.name == "ascendex":
            return AscendEX(
                exchange.api_key, exchange.api_secret, exchange.api_passphrase
            )
        elif exchange.name == "okx":
            return OKX(exchange.api_key, exchange.api_secret, exchange.api_passphrase)
