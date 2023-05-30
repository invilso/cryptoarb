from ..models import Exchange
from main.models import CoinPair, Order

from typing import TypedDict, Tuple
from django.db import transaction

import json

def read_json_file(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            if not isinstance(data, list):
                data = []
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
        with open(filename, 'w') as file:
            json.dump(data, file)
        return data

def append_to_json_file(filename, new_data):
    data = read_json_file(filename)
    data.append(new_data)
    with open(filename, 'w') as file:
        json.dump(data, file)

def clear_json_file(filename):
    data = []
    with open(filename, 'w') as file:
        json.dump(data, file)


class ProcessedData(TypedDict):
    bid: Tuple[float, float]
    ask: Tuple[float, float]
    quantity_usd_ask: float
    quantity_usd_bid: float


class BaseExchange:
    _price = None
    _price_depth = None
    _proxies: dict = None

    def __init__(self, api_key: str, api_secret: str, api_passphrase: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        
    def set_proxy(self, proxy: dict):
        self._proxies = proxy

    def preprocess_coin_pair(self, base_coin: str, quote_coin: str) -> str:
        return f"{base_coin}{quote_coin}"

    def get_order(self, orders: list) -> Tuple[float, float]:
        return orders[0]

    def convert_quantity_to_usd(
        self, order: Tuple[float, float], coin_pair: CoinPair
    ) -> float:
        raise NotImplementedError("This method should be implemented in child classes")

    def convert_quantity_to_usd_from_depth(
        self, order: Tuple[float, float], coin_pair: CoinPair
    ) -> float:
        if not self._price_depth:
            asks, bids = self.get_order_books(
                self.preprocess_coin_pair(coin_pair.base_coin, "USDT")
            )
            ask = self.get_order(asks)
            self._price_depth = ask[0]
        quantity_usd = self._price_depth * order[1]
        return quantity_usd

    def get_order_books(
        self, coin_pair: str
    ) -> Tuple[list[Tuple[float, float]], list[Tuple[float, float]]]:
        raise NotImplementedError("This method should be implemented in child classes")

    def process_data(
        self,
        bids: list[Tuple[float, float]],
        asks: list[Tuple[float, float]],
        coin_pair: CoinPair,
    ) -> ProcessedData:
        bid = self.get_order(bids)
        ask = self.get_order(asks)
        # such a number of nested try/excepts is a requirement of the customer
        try:
            quantity_usd_ask = self.convert_quantity_to_usd(
                order=ask, coin_pair=coin_pair
            )
        except Exception:
            try:
                quantity_usd_ask = self.convert_quantity_to_usd_from_depth(
                    order=ask, coin_pair=coin_pair
                )
            except Exception:
                quantity_usd_ask = None

        try:
            quantity_usd_bid = self.convert_quantity_to_usd(
                order=bid, coin_pair=coin_pair
            )
        except Exception:
            try:
                quantity_usd_bid = self.convert_quantity_to_usd_from_depth(
                    order=bid, coin_pair=coin_pair
                )
            except Exception:
                quantity_usd_bid = None
        processed_data: ProcessedData = {
            "bid": bid,
            "ask": ask,
            "quantity_usd_ask": quantity_usd_ask,
            "quantity_usd_bid": quantity_usd_bid,
        }
        return processed_data

    def apply_commission(self, data: ProcessedData, exchange: Exchange) -> ProcessedData:
        bid_with_commission = (
            data['bid'][0] + (data['bid'][0] * (exchange.buy_percentage / 100)),
            data['bid'][1] + (data['bid'][1] * (exchange.buy_percentage / 100))
        )
        ask_with_commission = (
            data['ask'][0] + (data['ask'][0] * (exchange.sell_percentage / 100)),
            data['ask'][1] + (data['ask'][1] * (exchange.sell_percentage / 100))
        )
        return {
            'bid': bid_with_commission,
            'ask': ask_with_commission,
            'quantity_usd_ask': data['quantity_usd_ask'],
            'quantity_usd_bid': data['quantity_usd_bid']
        }
        
    def update_in_db(
        self, processed_data: ProcessedData, exchange: Exchange, coin_pair: CoinPair
    ):
        order_ask = Order.objects.filter(
            exchange=exchange, coin_pair=coin_pair, order_type="ask"
        )
        order_ask.update(
            price=processed_data["ask"][0],
            quantity=processed_data["ask"][1],
            quantity_usd=processed_data["quantity_usd_ask"],
        )
        order_bid = Order.objects.filter(
            exchange=exchange, coin_pair=coin_pair, order_type="bid"
        )
        order_bid.update(
            price=processed_data["bid"][0],
            quantity=processed_data["bid"][1],
            quantity_usd=processed_data["quantity_usd_bid"],
        )
        
    def create_in_db(
        self, processed_data: ProcessedData, exchange: Exchange, coin_pair: CoinPair
    ):
        order_ask = Order.objects.create(
            exchange=exchange,
            coin_pair=coin_pair,
            price=processed_data["ask"][0],
            quantity=processed_data["ask"][1],
            quantity_usd=processed_data["quantity_usd_ask"],
            order_type="ask",
        )
        order_bid = Order.objects.create(
            exchange=exchange,
            coin_pair=coin_pair,
            price=processed_data["bid"][0],
            quantity=processed_data["bid"][1],
            quantity_usd=processed_data["quantity_usd_bid"],
            order_type="bid",
        )
        order_ask.save()
        order_bid.save()
        
    def save_data(
        self, processed_data: ProcessedData, exchange: Exchange, coin_pair: CoinPair
    ):  
        if Order.objects.filter(exchange=exchange, coin_pair=coin_pair).exists():
            self.update_in_db(processed_data=processed_data, exchange=exchange, coin_pair=coin_pair)
        else:
            self.create_in_db(processed_data=processed_data, exchange=exchange, coin_pair=coin_pair)
            
    def save_data_to_json(self, processed_data: ProcessedData, exchange: Exchange, coin_pair: CoinPair):
        data={
            'exchange': exchange.pk,
            'coin_pair': coin_pair.pk,
            'processed_data': processed_data,
        }
        append_to_json_file('data.json', data)



