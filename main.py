from tqdm import tqdm
from time import sleep
import os
import json
import requests
from dotenv import load_dotenv 
import pandas as pd
import datetime


load_dotenv()
funding_rates = []
tracker = set()
TOKEN_BOT = os.getenv('TOKEN_BOT')
CHAT_ID = os.getenv('CHAT_ID')
COINGLASS_APIKEY = os.getenv('COINGLASS_APIKEY') 

def send_telegram_message(message):
    try:
        telegram_url = f'https://api.telegram.org/bot{TOKEN_BOT}/sendMessage'
        params = {'chat_id': CHAT_ID, 'text': str(message)}
        response = requests.post(telegram_url, params=params)
        if response.status_code != 200:
            print(f'Failed to send message to Telegram. Error code: {response.status_code}')
        else:
            print('Message succesfully sent to Telegram.')
    except Exception as e:
        print(f"Error: {e}")


def reset_tracker_if_midnight():
    now = datetime.datetime.now()
    if now.hour == 0:
        global tracker
        tracker = set()
        print("Tracker reset at midnight.")




def fetch_funding_rates():
    try:
        url = "https://open-api.coinglass.com/public/v2/funding"
        headers = {
            "accept": "application/json",
            "coinglassSecret": COINGLASS_APIKEY
        }

        response = requests.get(url, headers=headers)
        data = response.json()

        if 'data' in data:
            data_list = data['data']
            #print(data_list)

            for item in tqdm(data_list, desc="Fetching rates..."):
                symbol = item['symbol']
                
                # Check if 'uMarginList' exists and has at least one element
                if 'uMarginList' in item and len(item['uMarginList']) > 0:
                    for items in item['uMarginList']:
                        # Check if 'rate' exists in the dictionary
                        if 'rate' in items:
                            funding_rate = items['rate']
                            exchange_name = items['exchangeName']

                else:
                    print(f"No uMarginList for symbol: {symbol}")
                    funding_rate = None
                    exchange_name = None

                if funding_rate is not None:
                    data = {
                    'symbol': symbol,
                    'funding_rate': funding_rate,
                    'exchange' : exchange_name
                    }

                    funding_rates.append(data)
    except Exception as e:
        print(f"Error {e}")


def fetch_lowest_rates():
    global tracker
    try:
        df = pd.DataFrame(funding_rates)
        lowest_funding = df[df['funding_rate'] <= -1.5]

        if lowest_funding.empty:
            print("No low funding perps")
        else:
            for index, row in tqdm(lowest_funding.iterrows(), desc="Processing low funding rate perps"):
                symbol = row['symbol']

                if symbol not in tracker:
                    message = f"Lowest Funding Perps:\n Symbol: {row['symbol']}, Funding Rate: {row['funding_rate']}, Exchange: {row['exchange']}\n"
                    send_telegram_message(message)

                    tracker.add(symbol)
        
    except Exception as e:
        print(f"Error {e}")



while True:
    fetch_funding_rates()
    fetch_lowest_rates()
    reset_tracker_if_midnight()
    print("Waiting 1 hour")
    sleep(60 * 60)
