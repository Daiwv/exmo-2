import time
import json
from src import api

# <params>

API_key, API_secret = open('keys.txt').read().split('\n')  # Your API and secret keys
# You can get it in exchange settings
work_time = 5  # time for work in minutes
candle_len = 1  # time of one candle in seconds
interval = 1  # interval between scanning the prices in seconds

# </params>

exmo = api.ExmoAPI(API_key, API_secret)

candles = []
prices = []

begin_time = time.time()
last_time = begin_time

while 1:
    price = float(exmo.req('ticker')['BTC_USD']['sell_price'])
    print('{:.2f}    {:.0f}'.format(prices[-1], time.time() - begin_time))
    time.sleep(interval)
    if time.time() - begin_time >= work_time * 60:
        break

with open('candles.json', 'w') as f:
    print(json.dumps(candles), file=f)
