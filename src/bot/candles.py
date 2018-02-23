import time
from root import root
from src.bot import exmo_api

# <params>

API_key, API_secret = open(root + '\data\keys.txt').read().split('\n')
# Your API and secret keys from Exmo settings, put it in keys.txt

work_time = 300  # time for work in minutes
candle_len = 30  # time of one candle in seconds
interval = 1  # interval between scanning the prices in seconds


# </params>


class Candles:
    def __init__(self, api_key, api_secret):
        self.exmo = exmo_api.ExmoAPI(api_key, api_secret)

    def make_candles(self, work_time, candle_len, interval):

        def make_candle(open_price):
            candle = {'open' : open_price,
                      'high' : open_price,
                      'low'  : open_price}

            begin_time = time.time()
            while time.time() - begin_time <= candle_len:
                # updating min and max of current candle
                price_now = float(self.exmo.req('ticker')['BTC_USD']['sell_price'])
                candle['high'] = max(candle['high'], price_now)
                candle['low'] = min(candle['low'], price_now)

                time.sleep(interval)

            price_now = float(self.exmo.req('ticker')['BTC_USD']['sell_price'])
            candle['close'] = price_now
            candle['high'] = max(candle['high'], price_now)
            candle['low'] = min(candle['low'], price_now)

            return candle

        begin_time = time.time()

        price_now = float(self.exmo.req('ticker')['BTC_USD']['sell_price'])
        candles = [make_candle(price_now)]

        while time.time() - begin_time <= work_time * 60:
            candles.append(make_candle(candles[-1]['close']))
            print('left:', work_time * 60 - (time.time() - begin_time))

        return candles


if __name__ == '__main__':
    # candles = Candles(API_key, API_secret).make_candles(work_time, candle_len, interval)
    # with open('candles.json', 'w') as f:
    #     print(json.dumps(candles), file=f)
    for i in range(60):
        begin_time = time.time()
        a = exmo_api.ExmoAPI(API_key, API_secret).req('ticker')['BTC_USD']['sell_price']
        print((time.time() - begin_time))
