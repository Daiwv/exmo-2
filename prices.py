import sys
import time
import api
import json

# <params>

my_public_API = 'UR key'
my_secret_API = 'UR key'
minutes = 10  # time for work in minutes
interval = 1  # time for interval between scanning in seconds

# </params>

exmo = api.ExmoAPI(my_public_API, my_secret_API)

prices = []

begin_time = time.time()

while 1:
    prices.append(float(exmo.req('ticker')['BTC_USD']['buy_price']))
    print('{:.2f}    {:.0f}'.format(prices[-1], time.time() - begin_time))
    time.sleep(interval)
    if time.time() - begin_time >= minutes * 60:
        break

with open('prices.json', 'w') as f:
    print(json.dumps(prices), file=f)
