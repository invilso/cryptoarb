from .base_exchange import BaseExchange
import json
from requests import Session
from main.models import CoinPair
from typing import Tuple


class Poloniex(BaseExchange):
    def __init__(self, api_key: str, api_secret: str, api_passphrase: str):
        self.client: Session = Session()
        self.client.proxies = self._proxies
        
        
    def preprocess_coin_pair(self, base_coin: str, quote_coin: str) -> str:
        return f"{quote_coin}_{base_coin}"

    def convert_quantity_to_usd(
        self, order: Tuple[float, float], coin_pair: CoinPair
    ) -> float:
        if coin_pair.quote_coin == "USDT":
            return float(order[1]) * float(order[0])
        if not self._price:
            symbol = f"USDT_{coin_pair.base_coin}"
            depth_raw = self.client.get(f'https://poloniex.com/public?command=returnTradeHistory&currencyPair={symbol}').text  # Получить стакан ордеров с лимитом 5
            depth = json.loads(depth_raw)
            price = float(depth[0]["rate"])
            self._price = price
        quantity_usd = float(order[1]) * self._price
        return quantity_usd

    def get_order_books(self, coin_pair: str) -> Tuple[list[Tuple[float, float]], list[Tuple[float, float]]]:
        depth_raw = self.client.get(f'https://poloniex.com/public?command=returnOrderBook&currencyPair={coin_pair}&depth=5').text  # Получить стакан ордеров с лимитом 5
        depth = json.loads(depth_raw)
        return depth["asks"], depth["bids"]