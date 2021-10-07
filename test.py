import os
from dotenv import load_dotenv
from binance.spot import Spot
import re

load_dotenv()

binance_api_key = os.getenv('BINANCE_API_KEY')
binance_api_secret = os.getenv('BINANCE_API_SECRET')

if __name__ == "__main__":

    client = Spot(key=binance_api_key, secret=binance_api_secret)
    print("SPOT balance:")
    for balance in client.account()['balances']:
        if re.fullmatch('0.(0)*', balance['free']) == None or re.fullmatch('0.(0)*', balance['locked']) == None:
            print(balance)

    print("liquidity pool:")
    for share in client.bswap_liquidity():
        if re.fullmatch('0', share['share']['sharePercentage']) == None:
            print(share)