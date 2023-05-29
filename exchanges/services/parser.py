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
    for coin_pair in chunk:
        errors = 0
        try:
            em = ExchangeManager()
            em.run_parse(coin_pair=CoinPair.objects.get(pk = coin_pair), exchange=Exchange.objects.get(pk = exchange), proxies=proxies)
        except Exception as e:
            errors = errors + 1
            tb = sys.exception().__traceback__
            print(f'EXCEPT: {e.with_traceback(tb)}')
        
        data_real = read_json_to_dict()
        
        data = {
            'iter_coins': data_real['iter_coins'] + 1,
            'iter_all_coins': get_all_iters(),
            'ended': False,
            'started': True,
            'start_time': data_real['start_time'],
            'parser_status': True, 
            'errors': data_real['errors'] + errors
        }
        
        if data['iter_all_coins'] == data['iter_coins']:
            data['ended'] = True
            data['started'] = False
            print(data_real['start_time'])
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
        data_real = read_json_to_dict()
        print(f'EXCEPT: {e}')
        data = {
            'iter_coins': data_real['iter_coins'],
            'iter_all_coins': get_all_iters(),
            'ended': False,
            'started': True,
            'start_time': data_real['start_time'],
            'parser_status': True,
            'errors': data_real['errors'] + 1
        }
        write_dict_to_json(data)
        
@shared_task
def main_loop():
    x = 0
    data = {
        'ended': False,
        'started': False,
        'parser_status': True
    }
    write_dict_to_json(data)
    while True:
        try:
            data = {
                'iter_coins': 0,
                'iter_all_coins': get_all_iters(),
                'ended': False,
                'started': True,
                'start_time': time.time(),
                'parser_status': True,
                'errors': 0
            }
            write_dict_to_json(data)
            exchanges = Exchange.objects.all()
            for i, exchange in enumerate(exchanges):
                exchange_thread.delay(exchange.pk)
                # t = Thread(target=exchange_thread, args=[exchange, em])
                # t.daemon = True
                # t.start()
                # exchange_thread(exchange)
                
            while True:
                data_real = read_json_to_dict()
                if data_real['iter_all_coins'] == data_real['iter_coins']:
                    break
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
        'ended': True,
        'started': False,
        'parser_status': False
    }
    write_dict_to_json(data)

#TODO add json file for profiling
@timer
def main():
    main_loop.delay()
    # t = Thread(target=main_loop)
    # t.daemon = True
    # t.start()
