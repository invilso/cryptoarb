from django.shortcuts import render
from binance.client import Client
from kucoin.client import Client as KuCoinClient

# Create your views here.
def BinanceView(request):
    api_key = 'YOUR_API_KEY'
    api_secret = 'YOUR_API_SECRET'

    client = Client(api_key, api_secret)

    symbol = 'ETHUSDT'  # Пример: курс Bitcoin к Tether
    depth = client.get_order_book(symbol=symbol, limit=5)  # Получить стакан ордеров с лимитом 5
    print(depth)

    print(f"Binance: {symbol}")
    print("Курс продажи:")
    for ask in depth['asks']:
        price, quantity = ask
        print(f"Цена: {price}, Количество: {quantity}")

    print("Курс покупки:")
    for bid in depth['bids']:
        price, quantity = bid
        print(f"Цена: {price}, Количество: {quantity}")
    
    
    context = {
        'depth': depth,
        'client': 'Binance',
        'symbol': symbol
    }
    
    return render(request, 'main/item.html', context)

def KuCoinView(request):
    api_key = 'YOUR_API_KEY'
    api_secret = 'YOUR_API_SECRET'
    api_passphrase = 'YOUR_API_PASSPHRASE'

    client = KuCoinClient(api_key, api_secret, api_passphrase)

    symbol = 'ETH-USDT'  # Пример: курс Bitcoin к Tether
    depth = client.get_order_book(symbol)  # Получить стакан ордеров с лимитом 5
    print(depth)
    print(f"KuCoin: {symbol}")
    print("Курс продажи:")
    x = 0
    for ask in depth['asks']:
        price, quantity = ask
        print(f"Цена: {price}, Количество: {quantity}")
        if x > 3:
            break
        x+=1

    print("Курс покупки:")
    x = 0
    for bid in depth['bids']:
        price, quantity = bid
        print(f"Цена: {price}, Количество: {quantity}")
        if x > 3:
            break
        x+=1
    context = {
        'depth': depth,
        'client': 'KuCoin',
        'symbol': symbol
    }
    return render(request, 'main/item.html', context)