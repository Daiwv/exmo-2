import time
import json
import tkinter

from root import root
from src.bot import api

# <params>

API_key, API_secret = open(root + '\data\keys.txt').read().split('\n')
# Your API and secret keys from Exmo settings, put it in keys.txt

work_time = 300  # time for work in minutes
candle_len = 30  # time of one candle in seconds
interval = 1  # interval between scanning the prices in seconds
response = 0.3  # time for getting response
ex_fee = 0.002  # exchange fee for every deal

# </params>


class Arbitrage:
    def __init__(self):
        f = open(root + '\data\loops_results.txt', 'w')
        self.pairs = json.load(open(root + '\data\pairs.json'))
        self.loops = json.load(open(root + '\data\loops.json'))
        self.exmo = api.ExmoAPI(API_key, API_secret)

    def run(self):
        while True:
            begin_time = time.time()

            self.prices = self.exmo.req('ticker')
            # handling exception
            if 'error' in self.prices:
                print(self.prices)
                continue

            max_profit, max_loop = 100, []
            for loop in self.loops:
                tmp = Arbitrage.checkLoop(loop)
                if tmp[0] > max_profit:
                    max_profit, max_loop = tmp

            # profit
            if max_profit > 100:
                print(max_profit, file=f)
                print(max_profit)
                print(max_loop, file=f)
                print(max_loop)

            time.sleep(max(0, begin_time + interval - time.time()))

        f.close()

    def convert(self, qt1, cur1, cur2):
        if [cur2, cur1] in self.pairs:
            price = float(self.prices[cur2 + '_' + cur1]['sell_price'])
            qt2 = qt1 / price
        else:
            price = float(self.prices[cur1 + '_' + cur2]['buy_price'])
            qt2 = qt1 * price
        return qt2 * (1 - ex_fee)

    def checkLoop(self, loop):
        max_profit = 100
        first = 0

        for num in range(3):
            now = 100

            for i in range(num, num + 3):
                cur1, cur2 = loop[i % 3], loop[(i + 1) % 3]
                now = self.convert(now, cur1, cur2)
            if now > max_profit:
                max_profit = now
                first = num

        return max_profit, loop[first:] + loop[:first]


if __name__ == '__main__':
    Arbitrage().run()
