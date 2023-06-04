import time
import traceback
from django.shortcuts import render
from binance.client import Client
from kucoin.client import Client as KuCoinClient
from .models import CoinPair, Order
from exchanges.services.parser import read_json_to_dict, main, write_dict_to_json
from cryptoarb.utils import log
from django.conf import settings
write_dict_to_json({'parser_status':False})

def calculate_spread_percentage(buy_price, sell_price):
    spread = sell_price - buy_price
    spread_percentage = ((sell_price - buy_price) / buy_price) * 100
    return spread_percentage

def get_best_price(currency_pair):
    orders = Order.objects.filter(coin_pair=currency_pair, quantity_usd__gt=49).order_by('price')

    if not orders.exists():
        return
    best_buy_price = orders.filter(order_type='ask').first()
    best_sell_price = orders.filter(order_type='bid').last()
    print(best_buy_price,best_sell_price)
    
    if not best_buy_price or not best_sell_price:
        return
    print(best_sell_price.exchange, currency_pair)
    data = {
        'currency_pair': currency_pair,
        'buy_exchange': best_buy_price.exchange,
        'sell_exchange': best_sell_price.exchange,
        'buy_bid': best_buy_price.price,
        'buy_ask': Order.objects.filter(coin_pair=currency_pair, exchange=best_buy_price.exchange, order_type='bid').last().price,
        'sell_bid': Order.objects.filter(coin_pair=currency_pair, exchange=best_sell_price.exchange, order_type='ask').last().price,
        'sell_ask': best_sell_price.price,
        'buy_volume': best_buy_price.quantity_usd,
        'sell_volume': best_sell_price.quantity_usd,
        'spread_percentage': calculate_spread_percentage(best_buy_price.price, best_sell_price.price)
    }
    return data

def MainView(request):
    try:
        if request.user.is_authenticated and request.user.is_active:
            
            status = read_json_to_dict()
            if not status['parser_status']:
                main()
                status['started_now'] = True
            else:
                timedelta = time.time() - status['start_time']
                if timedelta > 60:
                    main()
                    status['started_now'] = True 
        else:
            status = {'broken': True}
    except Exception as e:
        log(f'EXCEPT:\n {traceback.format_exc()} \n\n {e}')
        status = {'broken': True}
    data = []
    for coin in CoinPair.objects.all():
        d = get_best_price(coin)
        if d:
            data.append(d)
        
    print(data)
    sorted_data = sorted(data, key=lambda x: x['spread_percentage'], reverse=True)
    return render(request, 'main/list.html', {'data': sorted_data, 'status': status})
