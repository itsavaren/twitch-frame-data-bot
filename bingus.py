from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

def bingus_quote():

    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {
    'symbol':'BINGUS',
    'convert':'USD'
    }
    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': '4192ecf6-3a6b-45d6-9a11-875626a38d48',
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        price = data['data']['BINGUS']['quote']['USD']['price']

        binguses = 1 / price
        price = round(float(price), 6)
        return f'The current price of bingus is ${price}. You can buy {round(binguses)} bingus for 1 USD.'
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)