from .base_exchange import BaseExchange
import json
from requests import Session
from main.models import CoinPair
from typing import Tuple


class AscendEX(BaseExchange):
    def __init__(self, api_key: str, api_secret: str, api_passphrase: str):
        self.client: Session = Session()
        self.client.proxies = self._proxies
        
        
    def preprocess_coin_pair(self, base_coin: str, quote_coin: str) -> str:
        return f"{base_coin}/{quote_coin}"

    def convert_quantity_to_usd(
        self, order: Tuple[float, float], coin_pair: CoinPair
    ) -> float:
        if coin_pair.quote_coin == "USDT":
            return float(order[1]) * float(order[0])
        if not self._price:
            symbol = f"{coin_pair.base_coin}/USDT"
            depth_raw = self.client.get(f'https://ascendex.com/api/pro/v1/trades?symbol={symbol}').text  # Получить стакан ордеров с лимитом 5
            depth = json.loads(depth_raw)['data']['data']
            price = float(depth[0]["p"])
            self._price = price
        quantity_usd = float(order[1]) * self._price
        return quantity_usd

    def get_order_books(self, coin_pair: str) -> Tuple[list[Tuple[float, float]], list[Tuple[float, float]]]:
        depth_raw = self.client.get(f'https://ascendex.com/api/pro/v1/depth?symbol={coin_pair}').text  # Получить стакан ордеров с лимитом 5
        depth = json.loads(depth_raw)['data']['data']
        return depth["asks"], depth["bids"]