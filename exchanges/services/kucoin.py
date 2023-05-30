from .base_exchange import BaseExchange
from kucoin.client import Client
from main.models import CoinPair
from typing import Tuple


class KuCoin(BaseExchange):
    def __init__(self, api_key: str, api_secret: str, api_passphrase: str, proxies: dict):
        self.client: Client = Client(api_key, api_secret, api_passphrase, requests_params={'proxies': proxies})
        
    def preprocess_coin_pair(self, base_coin: str, quote_coin: str) -> str:
        return f"{base_coin}-{quote_coin}"

    def convert_quantity_to_usd(
        self, order: Tuple[float, float], coin_pair: CoinPair
    ) -> float:
        if coin_pair.quote_coin == "USDT":
            return float(order[1]) * float(order[0])
        if not self._price:
            price = self.client.get_ticker(symbol=f"{coin_pair.base_coin}-USDT")
            price = float(price["price"])
            self._price = price
        quantity_usd = float(order[1]) * self._price
        return quantity_usd

    def get_order_books(self, coin_pair: str) -> Tuple[list[Tuple[float, float]], list[Tuple[float, float]]]:
        depth = self.client.get_order_book(coin_pair)  # Получить стакан ордеров с лимитом 5
        return depth["asks"], depth["bids"]