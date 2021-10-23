import requests
import json
import sys

def _dump(file, namefile):
    with open(namefile, 'w') as outfile:
        json.dump(file, outfile)

def _load(namefile):
    with open(namefile) as json_file:
        return json.load(json_file)

def _get_rates(app_id, currency, namefile):
    """
    Get latest currency rates using openexchangerates API

    :param app_id:   string, the API ID required to use the API
    :param currency: string, the currency wanted
    :param namefile: string, the name of the file where we drop the API return call for caching
    :return:         float,  rate conversion to USD
    """
    try:
        r = requests.get('https://openexchangerates.org/api/latest.json?app_id={}'.format(app_id))
    except requests.exceptions.RequestException as e:
        sys.exit("Exception when getting latest currencies rates: {}".format(e))
    rates = r.json()['rates']
    _dump(rates, namefile)
    if currency not in rates:
        sys.exit("This currency ({}) is not supported, It has to be a 3-letter code: ".format(currency))
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
            sys.exit("This currency ({}) is not supported, It has to be a 3-letter code: ".format(currency))
        return cached_currency[currency]
    else:
        return _get_rates(currency=currency)
"""
coinmarketcap_api_key
"""
def _get_fiat(api_key, currency, namefile):
    """
    Get fiat using openexchangerates API

    :param api_key:  string, the API ID required to use the API
    :param currency: string, the currency wanted
    :param namefile: string, the name of the file where we drop the API return call for caching
    :return:         dict,   containing the name, symbol, sign and coinmarketcap id
    """
    headers = {'X-CMC_PRO_API_KEY': api_key}
    try:
        r = requests.get('https://pro-api.coinmarketcap.com/v1/fiat/map'.format(), headers=headers)
    except requests.exceptions.RequestException as e:
        sys.exit("Exception when getting latest currencies fiat: {}".format(e))
    if r.status_code != 200:
        sys.exit("Something went wrong with your call API: {}".format(r.status_code))
    fiat = r.json()['data']
    _dump(fiat, namefile)
    for f in fiat:
        if f['symbol'] == currency:
            return f
    sys.exit("This currency ({}) is not supported, It has to be a 3-letter code: ".format(currency))
  

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
        sys.exit("This currency ({}) is not supported, It has to be a 3-letter code: ".format(currency))
    else:
        return _get_fiat(currency)

def compute_holding(api_key, portfolio_filename, currency):
    """
    Compute the value of your portfolio given the quantity of each token owned

    :param api_key:            string,  the API key required to use the API
    :param portfolio_filename: string,  json file containing the info about your owned tokens
    :param currency:           string,  the currency wanted
    :return:                   dict,    containing the name, symbol, sign and coinmarketcap id
    """
    headers = {'X-CMC_PRO_API_KEY': api_key}
    payload = {'limit': '3000', 'sort': 'market_cap', 'convert': currency}
    try:
        r = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'.format(), headers=headers, params=payload)
    except requests.exceptions.RequestException as e:
        sys.exit("Something went wrong: {}".format(e))
    if r.status_code != 200:
        sys.exit("Something went wrong with your call API: {}\n{}".format(r.status_code, r.json()))
    try:
        currency_hold = _load(portfolio_filename)
    except FileNotFoundError:
        sys.exit("No {} file found".format(portfolio_filename))
    invested = currency_hold['invested']['quantity']
    sum = 0
    res = {}
    for cur in r.json()['data']:
        if cur['symbol'] in currency_hold['data']:
            hold = currency_hold['data'][cur['symbol']]
            value = cur['quote'][currency]['price'] * hold['quantity']
            sum += value
            res[cur['symbol']] = {
                'price': cur['quote'][currency]['price'],
                'quantity': hold['quantity'],
                'value': cur['quote'][currency]['price'] * hold['quantity'],
                'currency': currency,
            }
    res['total'] = {
        'value': sum,
        'currency': currency,
        'profit': sum - invested,
        'ROI': sum / invested
    }
    return res

# This API cache a lot and didn't found a way to refresh the value I get
def get_eth_wallet_balance(eth_address, currency):
    """
    Get the balance on a given ETH address

    :param eth_address: string, the ETH address
    :param currency:    string, the currency wanted
    :return:            int,    the balance of the ethereum address in the currency given
    """
    try:
        r = requests.get('https://api.blockchair.com/ethereum/dashboards/address/{}'.format(eth_address))
    except requests.exceptions.RequestException as e:
        sys.exit("Exception when getting ethereum wallet infos: {}".format(e))
    res = r.json()['data'][eth_address.lower()]['address']['balance_usd']
    return res * get_currency_rate(currency=currency)