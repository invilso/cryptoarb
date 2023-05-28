from .base_exchange import BaseExchange
from huobi.rest.client import HuobiRestClient as Client
from main.models import CoinPair
from typing import Tuple


class Huobi(BaseExchange):
    def __init__(self, api_key: str, api_secret: str, api_passphrase: str):
        self.client: Client = Client(api_key, api_secret)
        
    def preprocess_coin_pair(self, base_coin: str, quote_coin: str) -> str:
        return f"{base_coin}{quote_coin}".lower()

    def convert_quantity_to_usd(
        self, order: Tuple[float, float], coin_pair: CoinPair
    ) -> float:
        if coin_pair.quote_coin == "USDT":
            return float(order[1]) * float(order[0])
        if not self._price:
            res = self.client.market_detail_merged(symbol=f"{coin_pair.base_coin}-USDT")
            price = float(res.data['tick']['close'])
            self._price = price
            
        quantity_usd = float(order[1]) * self._price
        return quantity_usd

    def get_order_books(self, coin_pair: str) -> Tuple[list[Tuple[float, float]], list[Tuple[float, float]]]:
        res = self.client.market_depth(symbol=coin_pair)
        depth = res.data['tick']
        
        return depth["asks"], depth["bids"]