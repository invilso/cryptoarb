from celery import shared_task
import datetime
import requests

TOKEN = '5660072628:AAFWzMHIdZpmvKEnLpQqKxT4IzHcLsaCYHc'
CHANNEL = '@fortestsinvilso'

def send_telegram_message(token, chat_id, message, parse_mode = 'html'):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print(f"Failed to send message. Error code: {response.status_code}")
    else:
        print("Message sent successfully!")
        
@shared_task
def create_queryes():
    current_time = datetime.datetime.now()
    send_telegram_message(TOKEN, CHANNEL, current_time)
    with open('file.txt', 'a') as f:
        f.write(f"{current_time}: 228\n")
    return True