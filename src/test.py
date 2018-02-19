import time
import json
from src import api

# <params>

API_key, API_secret = open('keys.txt').read().split('\n')  # Your API and secret keys
# You can get it in exchange settings
minutes = 5  # time for work in minutes
interval = 1  # time for interval between scanning in seconds

# </params>

exmo = api.ExmoAPI(API_key, API_secret)

prices = []

begin_time = time.time()

while 1:
    prices.append(float(exmo.req('ticker')['BTC_USD']['sell_price']))
    print('{:.2f}    {:.0f}'.format(prices[-1], time.time() - begin_time))
    time.sleep(interval)
    if time.time() - begin_time >= minutes * 60:
        break

with open('prices.json', 'w') as f:
    print(json.dumps(prices), file=f)
