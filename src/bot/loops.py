import time
import json

from root import root
from src.bot import api

# <params>

API_key, API_secret = open(root + '\data\keys.txt').read().split('\n')
# Your API and secret keys from Exmo settings, put it in keys.txt

work_time = 300  # time for work in minutes
candle_len = 30  # time of one candle in seconds
interval = 0.33  # interval between scanning the prices in seconds
response = 0.3  # time for getting response
ex_fee = 0.002

# </params>


def triangle(x):
    ans = []
    for v in graph[x]:
        for u in graph[v]:
            if x in graph[u]:
                ans.append(set([x, v, u]))
    return ans


if __name__ == '__main__':
    exmo = api.ExmoAPI(API_key, API_secret)

    graph = {}
    currencies = exmo.req('currency')
    for i in currencies:
        graph[i] = []

    pairs = exmo.req('ticker')
    for i in pairs:
        print(i)
        cur1, cur2 = i.split('_')
        graph[cur1].append(cur2)
        graph[cur2].append(cur1)

    triangles = []

    for i in list(graph.keys()):
        update = triangle(i)
        for item in update:
            if item not in triangles:
                triangles.append(item)

    todump = []
    for i in triangles:
        a = []
        for j in i:
            a += [j]
        todump.append(tuple(a))
    print(todump)
    with open(root + '\data\loops.json', 'w') as f:
        json.dump(todump, f)
