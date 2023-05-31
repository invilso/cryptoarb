from .base_exchange import BaseExchange
import json
from requests import Session
from main.models import CoinPair
from typing import Tuple


class OKX(BaseExchange):        
    def preprocess_coin_pair(self, base_coin: str, quote_coin: str) -> str:
        return f"{base_coin}-{quote_coin}"

    def convert_quantity_to_usd(
        self, order: Tuple[float, float], coin_pair: CoinPair
    ) -> float:
        if coin_pair.quote_coin == "USDT":
            return float(order[1]) * float(order[0])
        if not self._price:
            symbol = f"{coin_pair.base_coin}-USDT"
            depth_raw = self.client.get(f'https://www.okx.com/api/v5/market/trades?instId={symbol}&limit=2').text
            depth = json.loads(depth_raw)['data']
            price = float(depth[0]["px"])
            self._price = price
        quantity_usd = float(order[1]) * self._price
        return quantity_usd

    def get_order_books(self, coin_pair: str) -> Tuple[list[Tuple[float, float]], list[Tuple[float, float]]]:
        self.client.proxies = {}
        depth_raw = self.client.get(f'https://www.okx.com/api/v5/market/books?instId={coin_pair}').text
        depth = json.loads(depth_raw)['data'][0]
        return depth["asks"], depth["bids"]