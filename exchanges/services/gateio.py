from .base_exchange import BaseExchange
import json
from main.models import CoinPair
from typing import Tuple


class GateIO(BaseExchange):        
    def preprocess_coin_pair(self, base_coin: str, quote_coin: str) -> str:
        return f"{base_coin}_{quote_coin}"

    def convert_quantity_to_usd(
        self, order: Tuple[float, float], coin_pair: CoinPair
    ) -> float:
        if coin_pair.quote_coin == "USDT":
            return float(order[1]) * float(order[0])
        if not self._price:
            quantity_usd = self.convert_quantity_to_usd_from_depth(order=order, coin_pair=coin_pair)
        return quantity_usd

    def get_order_books(self, coin_pair: str) -> Tuple[list[Tuple[float, float]], list[Tuple[float, float]]]:
        self.client.proxies = {}
        depth_raw = self.client.get(f'https://api.gateio.ws/api/v4/spot/order_book?currency_pair={coin_pair}&limit=1').text
        depth = json.loads(depth_raw)
        return depth["asks"], depth["bids"]