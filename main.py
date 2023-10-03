from tqdm import tqdm
from time import sleep
import os
import json
import requests
from dotenv import load_dotenv 
import pandas as pd

load_dotenv()
perps = [ 'BEL','SUI', '10000LADYS', '10000NFT', '1000BONK', '1000BTT', '1000FLOKI', '1000LUNC', '1000PEPE', '1000XEC', '1INCH', 'AAVE', 'ACH', 'ADA', 'AGIX', 'AGLD', 'AKRO', 'ALGO', 'ALICE', 'ALPACA', 'ALPHA', 'AMB', 'ANKR', 'ANT', 'APE', 'API3', 'APT', 'ARB', 'ARKM', 'ARK', 'ARPA', 'AR', 'ASTR', 'ATA', 'ATOM', 'AUCTION', 'AUDIO', 'AVAX', 'AXS', 'BADGER', 'BAKE', 'BAL', 'BAND', 'BAT', 'BCH', 'BEL', 'BICO', 'BLUR', 'BLZ', 'BNB', 'BNT', 'BNX', 'BOBA', 'BSV', 'BSW', 'BTC', 
'C98', 'CEEK', 'CELO', 'CELR', 'CFX', 'CHR', 'CHZ', 'CKB', 'COMBO', 'COMP', 'DOGE', 'DOT', 'DUSK', 'DYDX', 'EDU', 'EGLD', 'ENJ', 'ENS', 'EOS', 'ETC', 'ETH', 'FET', 'FIL', 'FITFI', 'FLM', 'FLOW', 'FLR', 'FORTH', 'FTM', 'FXS', 'GALA', 'GAL', 'GFT', 'GLMR', 'GLM', 'GMT', 'GMX', 'GPT', 'GRT', 'GTC', 'HBAR', 'HFT', 'HIGH', 'HNT', 'HOOK', 'HOT', 'ICP', 'ICX', 'IDEX', 'ID', 'ILV', 'IMX', 'INJ', 'IOST', 'IOTA', 'YGG', 'ZEC', 'ZEN', 'ZIL', 'ZRX', 'CRO', 'CRV', 'CTC', 'CTK', 'CTSI', 'CVC', 'CVX', 'CYBER', 'DAR', 'DASH', 'DENT', 'DGB', 'DODO', 'IOTX', 'JASMY', 'JOE', 'JST', 'KAS', 'KAVA', 'KDA', 'KEY', 'KLAY', 'KNC', 'KSM', 'LDO', 'LEVER', 'LINA', 'LINK', 'LIT', 'LOOKS', 'LPT', 'LQTY', 'LRC', 'LTC', 'LUNA2', 'MAGIC', 'MANA', 'MASK', 'MATIC', 'MAV', 'MC', 'MDT', 'MINA', 'MKR', 'MTL', 'NEAR', 'NEO', 'NKN', 'OCEAN', 'OGN', 'OMG', 'ONE', 'ONT', 'OP', 'ORDI', 'OXT', 'PAXG', 'PENDLE', 'PEOPLE', 'PHB', 'QNT', 'QTUM', 'RAD', 'RDNT', 'REEF', 'REN', 'REQ', 'RLC', 'RNDR', 'ROSE', 'RPL', 'RSR', 'RSS3', 'RUNE', 'RVN', 'SAND', 'SCRT', 'SC', 'SEI', 'SFP', 'SHIB1000', 'SKL', 'SLP', 'SNX', 'SOL', 'SPELL', 'SSV', 'STG', 'STMX', 'STORJ', 'STX', 
'SUI', 'SUN', 'SUSHI', 'SWEAT', 'SXP', 'THETA', 'TLM', 'TOMO', 'TRB', 'TRU', 'TRX', 'T', 'TWT', 'UMA', 'UNFI', 'UNI', 'VET', 'VGX', 'WAVES', 'WLD', 'WOO', 'XCN', 'XEM', 'XLM', 'XMR', 'XNO', 
'XRP', 'XTZ', 'XVG', 'YFII', 'YFI', 'CORE', 'COTI', 'FRONT', 'DEFI']
funding_rates = []
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
    except Exception as e:
        print(f"Error: {e}")



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
    prev_message = ''

    try:
        df = pd.DataFrame(funding_rates)
        lowest_funding = df[df['funding_rate'] <= -1.5]

        if lowest_funding.empty:
            print("No low funding perps")
            pass
        else:
            message = "Lowest Funding Perps:\n"
            for index, row in tqdm(lowest_funding.iterrows(), desc="Processing low funding rate perps"):
                symbol = row['symbol']
                message += f"Symbol: {row['symbol']}, Funding Rate: {row['funding_rate']}, Exchange: {row['exchange']}\n"

            if message != prev_message:
                prev_message = message
                # Send the formatted message to Telegram
                send_telegram_message(message)
    except Exception as e:
        print(f"Error {e}")



while True:
    fetch_funding_rates()
    fetch_lowest_rates()
    print("Waiting 2 hours")
    sleep(15)
    #sleep(60 * 60 * 2)
