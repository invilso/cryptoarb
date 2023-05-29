import time
from django.shortcuts import render
from binance.client import Client
from kucoin.client import Client as KuCoinClient
from .models import CoinPair, Order
from exchanges.services.parser import read_json_to_dict, main, write_dict_to_json
write_dict_to_json({'parser_status':False})

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
        print(e)
        status = {'broken': True}
    data = []
    for coin in CoinPair.objects.all():
        ask_min = Order.objects.filter(coin_pair__pk = coin.pk, order_type = 'ask', quantity_usd__gte=50).order_by('-price').first()
        bid_max = Order.objects.filter(coin_pair__pk = coin.pk, order_type = 'bid', quantity_usd__gte=50).order_by('price').first()
        # if ask_min.quantity_usd < 51 or bid_max.quantity_usd < 51:
        #     continue
        bid_min = Order.objects.filter(coin_pair__pk = coin.pk, exchange__pk = ask_min.exchange.pk, order_type = 'bid').first().price
        ask_max = Order.objects.filter(coin_pair__pk = coin.pk, exchange__pk = bid_max.exchange.pk, order_type = 'ask').first().price
        spread = ((bid_max.price - ask_min.price) / ask_min.price) * 100
        data.append(
            {
                'coin_pair': coin,
                'ask_min': ask_min,
                'ask_max': ask_max,#
                'bid_max': bid_max,
                'bid_min': bid_min,#
                'spread': spread
            }
        )
        
    sorted_data = sorted(data, key=lambda x: x['spread'], reverse=True)
    return render(request, 'main/list.html', {'data': sorted_data, 'status': status})
