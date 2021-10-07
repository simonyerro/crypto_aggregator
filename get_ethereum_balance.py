#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

eth_address = os.getenv('ETHEREUM_ADDRESS')
openexchangerates_app_id = os.getenv('OPENEXCHANGERATES_APP_ID')

def _dump(mails, namefile='currencies.json'):
    with open(namefile, 'w') as outfile:
        json.dump(mails, outfile)

def _load(namefile='currencies.json'):
    with open(namefile) as json_file:
        return json.load(json_file)

def _get_rates(currency='USD'):
    try:
        r = requests.get('https://openexchangerates.org/api/latest.json?app_id={}'.format(openexchangerates_app_id))
    except requests.exceptions.RequestException as e:
        raise SystemExit("Exception when getting latest currencies rates: {}".format(e))
    rates = r.json()['rates']
    _dump(rates)
    if currency not in rates:
        raise SystemExit("This currency ({}) is not supported, It has to be a 3-letter code: ".format(currency))
    return rates[currency]

def get_currency_rate(cache=True, currency='USD'):
    currency = currency.upper()
    if currency == 'USD':
        return 1
    if cache:
        try:
            cached_currency = _load()
        except FileNotFoundError:
            return _get_rates(currency=currency)   
        if currency not in cached_currency:
            raise SystemExit("This currency ({}) is not supported, It has to be a 3-letter code: ".format(currency))
        return cached_currency[currency]
    else:
        return _get_rates(currency=currency)

def get_eth_wallet_balance(eth_address, currency='USD'):
    try:
        r = requests.get('https://api.blockchair.com/ethereum/dashboards/address/{}'.format(eth_address))
    except requests.exceptions.RequestException as e:
        raise SystemExit("Exception when getting ethereum wallet infos: {}".format(e))
    res = r.json()['data'][eth_address.lower()]['address']['balance_usd']
    return res * get_currency_rate(currency=currency)

if __name__ == "__main__":
    print(get_eth_wallet_balance(eth_address, currency='EUR'))

