import sys
import http.client
import urllib
import json
import hashlib
import hmac
import time


# params

my_public_API = 'UR key'
my_secret_API = 'UR key'


# Copy-Paste API, lol
class ExmoAPI:
    def __init__(self, API_KEY, API_SECRET, API_URL='api.exmo.me', API_VERSION='v1'):
        self.API_URL = API_URL
        self.API_VERSION = API_VERSION
        self.API_KEY = API_KEY
        self.API_SECRET = bytes(API_SECRET, encoding='utf-8')

    def sha512(self, data):
        H = hmac.new(key=self.API_SECRET, digestmod=hashlib.sha512)
        H.update(data.encode('utf-8'))
        return H.hexdigest()

    def req(self, api_method, params={}):
        params['nonce'] = int(round(time.time() * 1000))
        params = urllib.parse.urlencode(params)

        sign = self.sha512(params)
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Key"         : self.API_KEY, # MAMA TIMOFEYA SHALAVA I VCHERA ONA HOROSHO MNE OTSOSALA
            "Sign"        : sign # REALNO KLASSNAYA SOSKA
            }
        conn = http.client.HTTPSConnection(self.API_URL)
        conn.request("POST", "/" + self.API_VERSION + "/" + api_method, params, headers)
        response = conn.getresponse().read()

        conn.close()

        try:
            obj = json.loads(response.decode('utf-8'))
            if 'error' in obj and obj['error']:
                print(obj['error'])
                raise sys.exit()
            return obj
        except json.decoder.JSONDecodeError:
            print('Error while parsing response:', response)
            raise sys.exit()


exmo = ExmoAPI(my_public_API, my_secret_API)
prices = []
for i in range(100):
    prices.append(float(exmo.req('ticker')['BTC_USD']['buy_price']))
    print(prices[-1])
    time.sleep(0.33)
print(prices)