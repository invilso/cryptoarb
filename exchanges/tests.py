from typing import Iterable
from django.test import TestCase
from main.models import CoinPair, Exchange
from exchanges.services.base_exchange import ProcessedData
from exchanges.services.mexc import MEXC

class BaseExchangeTestCase(TestCase):
    def setUp(self):
        # Создайте здесь необходимые объекты для тестирования
        self.exchange = Exchange.objects.create(name='mexc')
        self.coin_pair = CoinPair.objects.create(base_coin='BTC', quote_coin='USDT')
        self.base_exchange = MEXC(api_key='test_key', api_secret='test_secret', api_passphrase='test_pass', proxies={})

    def test_process_data(self):
        bids = [(100, 1), (200, 2), (300, 3)]
        asks = [(400, 4), (500, 5), (600, 6)]

        processed_data = self.base_exchange.process_data(bids, asks, self.coin_pair)

        self.assertIsInstance(processed_data, ProcessedData)
        self.assertEqual(len(processed_data), 4)
        self.assertIn('bid', processed_data)
        self.assertIn('ask', processed_data)
        self.assertIn('quantity_usd_ask', processed_data)
        self.assertIn('quantity_usd_bid', processed_data)

    def test_apply_commission(self):
        data = {
            'bid': (100, 1),
            'ask': (200, 2),
            'quantity_usd_ask': 1000,
            'quantity_usd_bid': 2000
        }
        commission = self.exchange.buy_percentage  # Замените на необходимую комиссию

        processed_data_with_commission = self.base_exchange.apply_commission(data, self.exchange)

        self.assertIsInstance(processed_data_with_commission, ProcessedData)
        self.assertEqual(len(processed_data_with_commission), 4)
        self.assertIn('bid', processed_data_with_commission)
        self.assertIn('ask', processed_data_with_commission)
        self.assertIn('quantity_usd_ask', processed_data_with_commission)
        self.assertIn('quantity_usd_bid', processed_data_with_commission)

        expected_bid = (100 + (100 * (commission / 100)), 1 + (1 * (commission / 100)))
        expected_ask = (200 + (200 * (commission / 100)), 2 + (2 * (commission / 100)))

        self.assertEqual(processed_data_with_commission['bid'], expected_bid)
        self.assertEqual(processed_data_with_commission['ask'], expected_ask)

    def test_preprocess_coin_pair(self):
        base_coin = 'BTC'
        quote_coin = 'USDT'

        processed_coin_pair = self.base_exchange.preprocess_coin_pair(base_coin, quote_coin)

        expected_coin_pair = f"{base_coin}{quote_coin}"

        self.assertEqual(processed_coin_pair, expected_coin_pair)

    def test_convert_quantity_to_usd(self):
        order = (10, 2)
        coin_pair = CoinPair(base_coin='BTC', quote_coin='USDT')

        quantity_usd = self.base_exchange.convert_quantity_to_usd(order, coin_pair)

        expected_quantity_usd = float(order[1]) * float(order[0])

        self.assertEqual(quantity_usd, expected_quantity_usd)

    def test_convert_quantity_to_usd_with_depth(self):
        order = (10, 2)
        coin_pair = CoinPair(base_coin='BTC', quote_coin='USDT')
        self.base_exchange._price = 500

        quantity_usd = self.base_exchange.convert_quantity_to_usd(order, coin_pair)

        expected_quantity_usd = 500 * float(order[0])

        self.assertEqual(quantity_usd, expected_quantity_usd)

    def test_get_order_books(self):
        coin_pair = 'BTCUSDT'

        asks, bids = self.base_exchange.get_order_books(coin_pair)

        self.assertIsInstance(asks, list)
        self.assertIsInstance(bids, list)
        self.assertTrue(len(asks) > 0)
        self.assertTrue(len(bids) > 0)
        self.assertIsInstance(asks[0], Iterable)
        self.assertIsInstance(bids[0], Iterable)
        self.assertEqual(len(asks[0]), 2)
        self.assertEqual(len(bids[0]), 2)
        self.assertIsInstance(asks[0][0], float)
        self.assertIsInstance(asks[0][1], float)
        self.assertIsInstance(bids[0][0], float)
        self.assertIsInstance(bids[0][1], float)