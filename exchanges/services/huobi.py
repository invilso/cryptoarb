import json
from requests import Session
from .base_exchange import BaseExchange
from main.models import CoinPair
from typing import Tuple


class Huobi(BaseExchange):
    def __init__(self, api_key: str, api_secret: str, api_passphrase: str, proxies: dict):
        self.client: Session = Session()
        self._proxies = proxies
        self.client.proxies = self._proxies
        
    def preprocess_coin_pair(self, base_coin: str, quote_coin: str) -> str:
        return f"{base_coin}{quote_coin}".lower()

    def convert_quantity_to_usd(
        self, order: Tuple[float, float], coin_pair: CoinPair
    ) -> float:
        if coin_pair.quote_coin == "USDT":
            return float(order[1]) * float(order[0])
        if not self._price:
            depth_raw = self.client.get(f'https://api.huobi.pro/market/trade?symbol={coin_pair.base_coin}usdt').text
            price = json.loads(depth_raw)['tick']['data'][0]
            price = float(price['price'])
            self._price = price
            
        quantity_usd = float(order[1]) * self._price
        return quantity_usd

    def get_order_books(self, coin_pair: str) -> Tuple[list[Tuple[float, float]], list[Tuple[float, float]]]:
        depth_raw = self.client.get(f'https://api.huobi.pro/market/depth?symbol={coin_pair}&type=step0').text
        depth = json.loads(depth_raw)['tick']
        return depth["asks"], depth["bids"]