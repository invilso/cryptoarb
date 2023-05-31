from .base_exchange import BaseExchange
from binance.client import Client
from main.models import CoinPair
from typing import Tuple


class Binance(BaseExchange):
    def _set_api_instance(self) -> None:
        self.client: Client = Client(self.api_key, self.api_secret, requests_params={'proxies': self._proxies})
    
    def convert_quantity_to_usd(
        self, order: Tuple[float, float], coin_pair: CoinPair
    ) -> float:
        if coin_pair.quote_coin == "USDT":
            return float(order[1]) * float(order[0])
        if not self._price:
            price = self.client.get_symbol_ticker(symbol=f"{coin_pair.base_coin}USDT")
            price = float(price["price"])
            self._price = price
        quantity_usd = float(order[1]) * self._price
        return quantity_usd
    
    def get_order_books(
        self,
        coin_pair: str,
    ) -> Tuple[list[Tuple[float, float]], list[Tuple[float, float]]]:
        depth = self.client.get_order_book(symbol=coin_pair)
        return depth["asks"], depth["bids"]
