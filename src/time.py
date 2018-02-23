import time
from src import exmo_api

# <params>

API_key, API_secret = open('keys.txt').read().split('\n')
# Your API and secret keys from Exmo settings, put it in keys.txt

work_time = 300  # time for work in minutes
candle_len = 30  # time of one candle in seconds
interval = 1  # interval between scanning the prices in seconds
response = 0.3  # time for get response for request

# </params>

exmo = exmo_api.ExmoAPI(API_key, API_secret)

if __name__ == '__main__':
    ans = []
    for i in range(60):
        begin_time = time.time()
        exmo.req('ticker')['BTC_USD']['sell_price']
        response_time = time.time() - begin_time
        print(response_time)
        ans.append(response_time)
    print('avg:', sum(ans) / 60)
