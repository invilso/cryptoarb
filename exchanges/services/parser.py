from .exchange_manager import ExchangeManager
from ..models import Exchange
from main.models import CoinPair
from threading import Thread
import time
import json
from .base_exchange import read_json_file, clear_json_file, BaseExchange
from typing import Dict, Any
import sys
from celery import shared_task


def write_dict_to_json(data: Dict[str, Any], filename: str = "status.json") -> None:
  """Write a dictionary to a JSON file.

  Args:
    data: A dictionary to write to the file.
    filename: The name of the JSON file. Defaults to "status.json".

  Returns:
    None
  """
  with open(filename, "w") as f:
    json.dump(data, f)

def read_json_to_dict(filename: str = "status.json") -> Dict[str, Any]:
  """Read a JSON file and return a dictionary.

  Args:
    filename: The name of the JSON file. Defaults to "status.json".

  Returns:
    A dictionary with the data from the file.
  """
  with open(filename, "r") as f:
    data = json.load(f)
  return data


def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Функция {func.__name__} выполнилась за {execution_time} секунд")
        return result

    return wrapper

def split_into_chunks(lst, chunk_size):
    return [lst[i:i+chunk_size] for i in range(0, len(lst), chunk_size)]
    
def get_all_iters():
    x = 0
    coins = CoinPair.objects.all()
    for coin in coins:
        x += len(coin.supported_exchanges.all())
    return x

@shared_task
def coin_thread(chunk: list, exchange: int, proxies: dict[str, str]):
    global ITER_COINS
    global ERRORS
    for coin_pair in chunk:
        try:
            em = ExchangeManager()
            em.run_parse(coin_pair=CoinPair.objects.get(pk = coin_pair), exchange=Exchange.objects.get(pk = exchange), proxies=proxies)
        except Exception as e:
            ERRORS = ERRORS + 1
            tb = sys.exception().__traceback__
            print(f'EXCEPT: {e.with_traceback(tb)}')
        
        ITER_COINS = ITER_COINS + 1
        data = {
            'iter_coins': ITER_COINS,
            'iter_all_coins': ITER_ALL_COINS,
            'ended': False,
            'started': True,
            'start_time': START_TIME,
            'parser_status': True, 
            'errors': ERRORS
        }
        if ITER_COINS == ITER_ALL_COINS:
            data['ended'] = True
            data['started'] = False
            print(time.time() - START_TIME)
        write_dict_to_json(data)
        
@shared_task
def exchange_thread(exchange: int):
    try:
        coins = CoinPair.objects.all()
        coins_ids = []
        for coin in coins:
            coins_ids.append(coin.pk)
        chunks = split_into_chunks(coins_ids, 3)
        for i, chunk in enumerate(chunks):
            proxies = {
                'http': f'socks5://username{i}:password{i}@localhost:9050',
                'https': f'socks5://username{i}:password{i}@localhost:9050'
            }
            coin_thread.delay(chunk, exchange, proxies)
            # t = Thread(target=coin_thread, args=[chunk, exchange, em, proxies])
            # t.daemon = True
            # t.start()
    except Exception as e:
        global ERRORS
        ERRORS = ERRORS + 1
        print(f'EXCEPT: {e}')
        data = {
            'iter_coins': ITER_COINS,
            'iter_all_coins': ITER_ALL_COINS,
            'ended': False,
            'started': True,
            'start_time': START_TIME,
            'parser_status': True, 
            'errors': ERRORS
        }
        write_dict_to_json(data)
        
@shared_task
def main_loop():
    global ITER_COINS
    global ITER_ALL_COINS
    global START_TIME
    global ERRORS
    x = 0
    data = {
        'ended': False,
        'started': False,
        'parser_status': True
    }
    write_dict_to_json(data)
    while True:
        try:
            ERRORS = 0
            ITER_COINS = 0
            ITER_ALL_COINS = get_all_iters()
            START_TIME = time.time()
            exchanges = Exchange.objects.all()
            for i, exchange in enumerate(exchanges):
                exchange_thread.delay(exchange.pk)
                # t = Thread(target=exchange_thread, args=[exchange, em])
                # t.daemon = True
                # t.start()
                # exchange_thread(exchange)
            
            while ITER_ALL_COINS != ITER_COINS and ITER_ALL_COINS != 0:
                time.sleep(1)
        except Exception as e:
            print('Omg')
            print(e)
        data = read_json_file('data.json')
        for v in data:
            be = BaseExchange('dada', 'dadasas', 'asdasdasas')
            be.save_data_to_db(exchange=Exchange.objects.get(pk = v['exchange']), coin_pair=CoinPair.objects.get(pk = v['coin_pair']), processed_data=v['processed_data'])
        clear_json_file('data.json')
        time.sleep(5)
        x+=1
        print(x)
        if x > 5:
            break
    data = {
        'iter_coins': ITER_COINS,
        'iter_all_coins': ITER_ALL_COINS,
        'ended': True,
        'started': False,
        'start_time': START_TIME,
        'parser_status': False,
        'errors': ERRORS
    }
    write_dict_to_json(data)

#TODO add json file for profiling
@timer
def main():
    main_loop.delay()
    # t = Thread(target=main_loop)
    # t.daemon = True
    # t.start()
