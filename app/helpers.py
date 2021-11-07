"""
Bunch of function to:
* communicate with coinmarketcap API
* communicate with openexchangerates API
* Load and dump json files
* Compute rates of your portfolio given your quantity of each token
"""

import json
import sys
import requests

COINMARKETCAP_API_URL = 'https://pro-api.coinmarketcap.com/v1'

def _dump(file, namefile):
    with open(namefile, 'w', encoding='UTF-8') as outfile:
        json.dump(file, outfile)

def _load(namefile):
    with open(namefile, encoding='UTF-8') as json_file:
        try:
            json_file = json.load(json_file)
        except ValueError as error:
            sys.exit(f"Something went wrong when loading your json file: {error}")
        return json_file

def _get_map(app_id, namefile):
    """
    Get mapping of symbols and slug to unique coinmarketcap id

    :param app_id:   string, the API ID required to use the API
    :param namefile: string, the name of the file where we drop the API return call for caching
    :return:         dict,  mapping of the symbols to unique coinmaketcap id
    """
    headers = {'X-CMC_PRO_API_KEY': app_id}
    url = f"{COINMARKETCAP_API_URL}/cryptocurrency/map"
    try:
        res = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as error:
        sys.exit(f"Something went wrong: {error}")
    if res.status_code != 200:
        sys.exit(f"Something went wrong with your call API: {res.status_code}\n{res.json()}")
    map_id = res.json()['data']
    _dump(map_id, namefile)
    return map_id

def _get_rates(app_id, currency, namefile):
    """
    Get latest currency rates using openexchangerates API

    :param app_id:   string, the API ID required to use the API
    :param currency: string, the currency wanted
    :param namefile: string, the name of the file where we drop the API return call for caching
    :return:         float,  rate conversion to USD
    """
    try:
        res = requests.get(f"https://openexchangerates.org/api/latest.json?app_id={app_id}")
    except requests.exceptions.RequestException as error:
        sys.exit(f"Exception when getting latest currencies rates: {error}")
    rates = res.json()['rates']
    _dump(rates, namefile)
    if currency not in rates:
        sys.exit(f"This currency ({currency}) is not supported, It has to be a 3-letter code: ")
    return rates[currency]

def get_currency_rate(app_id, cache, currency, namefile):
    """
    Hat function which calls _get_rates if cache is False
    or the dumped file if cache is True

    :param app_id:   string,  the API ID required to use the API
    :param cache:    boolean, indicate if get the cached version or make a new API call
    :param currency: string,  the currency wanted
    :param namefile: string,  the name of the file where we drop the API return call for caching
    :return:         float,   rate conversion to USD
    """
    currency = currency.upper()
    if currency == 'USD':
        return 1
    if cache:
        try:
            cached_currency = _load(namefile)
        except FileNotFoundError:
            return _get_rates(app_id, currency, namefile)
        if currency not in cached_currency:
            sys.exit(f"This currency ({currency}) is not supported, It has to be a 3-letter code: ")
        return cached_currency[currency]
    else:
        return _get_rates(app_id, currency, namefile)

def _get_fiat(api_key, currency, namefile):
    """
    Get fiat using openexchangerates API

    :param api_key:  string, the API ID required to use the API
    :param currency: string, the currency wanted
    :param namefile: string, the name of the file where we drop the API return call for caching
    :return:         dict,   containing the name, symbol, sign and coinmarketcap id
    """
    headers = {'X-CMC_PRO_API_KEY': api_key}
    url = f"{COINMARKETCAP_API_URL}/fiat/map"
    try:
        res = requests.get(url, headers=headers)
    except requests.exceptions.RequestException as error:
        sys.exit(f"Exception when getting latest currencies fiat: {error}")
    if res.status_code != 200:
        sys.exit(f"Something went wrong with your call API: {res.status_code}")
    fiats = res.json()['data']
    _dump(fiats, namefile)
    for fiat in fiats:
        if fiat['symbol'] == currency:
            return fiat
    sys.exit("This currency ({currency}) is not supported, It has to be a 3-letter code: ")

def get_currency_fiat(api_key, cache, currency, namefile):
    """
    Hat function which calls _get_fiat if cache is False
    or the dumped file if cache is True

    :param api_key:   string, the API key required to use the API
    :param cache:    boolean, indicate if get the cached version or make a new API call
    :param currency: string,  the currency wanted
    :param namefile: string,  the name of the file where we drop the API return call for caching
    :return:         dict,    containing the name, symbol, sign and coinmarketcap id
    """
    currency = currency.upper()
    if cache:
        try:
            cached_currency = _load(namefile)
        except FileNotFoundError:
            return _get_fiat(api_key, currency, namefile)
        for cur in cached_currency:
            if cur['symbol'] == currency:
                return cur
        sys.exit(f"This currency ({currency}) is not supported, It has to be a 3-letter code")
    else:
        return _get_fiat(api_key, currency, namefile)

def compute_holding(api_key, portfolio, currency):
    """
    Compute the value of your portfolio given the quantity of each token owned

    :param api_key:            string,  the API key required to use the API
    :param portfolio_filename: dict,  dict containing the info about your owned tokens
    :param currency:           string,  the currency wanted
    :return:                   dict,    value of each coins holded
    """

    slugs = ','.join(portfolio['data'][el]['slug'] for el in portfolio['data'])
    headers = {'X-CMC_PRO_API_KEY': api_key}
    payload = {'slug': slugs, 'convert': currency}
    url = f"{COINMARKETCAP_API_URL}/cryptocurrency/quotes/latest"

    try:
        res = requests.get(url, headers=headers, params=payload)
    except requests.exceptions.RequestException as error:
        sys.exit(f"Something went wrong: {error}")
    if res.status_code != 200:
        sys.exit(f"Something went wrong with your call API: {res.status_code}\n{res.json()}")
    invested = portfolio['invested']['quantity']
    sum_, res, quotes = 0, {}, res.json()['data']
    for cur in quotes:
        hold = portfolio['data'][quotes[cur]['slug']]
        value = quotes[cur]['quote'][currency]['price'] * hold['quantity']
        sum_ += value
        res[quotes[cur]['symbol']] = {
            'price': quotes[cur]['quote'][currency]['price'],
            'quantity': hold['quantity'],
            'value': quotes[cur]['quote'][currency]['price'] * hold['quantity'],
            'currency': currency,
        }
    res['total'] = {
        'value': sum_,
        'currency': currency,
        'profit': sum_ - invested,
        'ROI': sum_ / invested
    }
    return res

# This API cache a lot and didn't found a way to refresh the value I get
# def get_eth_wallet_balance(eth_address, currency):
#     """
#     Get the balance on a given ETH address

#     :param eth_address: string, the ETH address
#     :param currency:    string, the currency wanted
#     :return:            int,    the balance of the ethereum address in the currency given
#     """
#     try:
#         res = requests.get(f"https://api.blockchair.com/ethereum/dashboards/address/{eth_address}")
#     except requests.exceptions.RequestException as error:
#         sys.exit(f"Exception when getting ethereum wallet infos: {error}")
#     res = res.json()['data'][eth_address.lower()]['address']['balance_usd']
#     return res * get_currency_rate(currency=currency)