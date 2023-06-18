from typing import Iterable
from django.test import TestCase
from main.models import CoinPair, Exchange
from exchanges.services.base_exchange import ProcessedData
from exchanges.services.mexc import MEXC
from exchanges.services.lbank import LBank
from exchanges.services.gateio import GateIO

class BaseExchangeTestCase(TestCase):
    def setUp(self):
        # Создайте здесь необходимые объекты для тестирования
        self.exchange = Exchange.objects.create(name='mexc')
        self.coin_pair = CoinPair.objects.create(base_coin='BTC', quote_coin='USDT')
        self.base_exchange = MEXC(api_key='test_key', api_secret='test_secret', api_passphrase='test_pass', proxies={})

    def test_get_order_books(self):
        coin_pair = self.base_exchange.preprocess_coin_pair(self.coin_pair.base_coin, self.coin_pair.quote_coin)

        asks, bids = self.base_exchange.get_order_books(coin_pair)

        self.assertIsInstance(asks, list)
        self.assertIsInstance(bids, list)
        self.assertTrue(len(asks) > 0)
        self.assertTrue(len(bids) > 0)
        self.assertIsInstance(asks[0], Iterable)
        self.assertIsInstance(bids[0], Iterable)
        self.assertEqual(len(asks[0]), 2)
        self.assertEqual(len(bids[0]), 2)
        self.assertIsInstance(asks[0][0], str)
        self.assertIsInstance(asks[0][1], str)
        self.assertIsInstance(bids[0][0], str)
        self.assertIsInstance(bids[0][1], str)
        
        
        
class LbankExchangeTestCase(BaseExchangeTestCase):
    def setUp(self):
        # Создайте здесь необходимые объекты для тестирования
        self.exchange = Exchange.objects.create(name='lbank')
        self.coin_pair = CoinPair.objects.create(base_coin='BTC', quote_coin='USDT')
        self.base_exchange = LBank(api_key='test_key', api_secret='test_secret', api_passphrase='test_pass', proxies={})

    def test_get_order_books(self):
        super().test_get_order_books()
        
class GateIOExchangeTestCase(BaseExchangeTestCase):
    def setUp(self):
        # Создайте здесь необходимые объекты для тестирования
        self.exchange = Exchange.objects.create(name='gateio')
        self.coin_pair = CoinPair.objects.create(base_coin='BTC', quote_coin='USDT')
        self.base_exchange = GateIO(api_key='test_key', api_secret='test_secret', api_passphrase='test_pass', proxies={})

    def test_get_order_books(self):
        super().test_get_order_books()