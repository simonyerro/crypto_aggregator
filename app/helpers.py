import requests
import json
import sys

COINMARKETCAP_API_URL = 'https://pro-api.coinmarketcap.com/v1'

def _dump(file, namefile):
    with open(namefile, 'w') as outfile:
        json.dump(file, outfile)

def _load(namefile):
    with open(namefile) as json_file:
        return json.load(json_file)

def _get_map(app_id, namefile):
    """
    Get mapping of symbols and slug to unique coinmarketcap id

    :param app_id:   string, the API ID required to use the API
    :param namefile: string, the name of the file where we drop the API return call for caching
    :return:         dict,  mapping of the symbols to unique coinmaketcap id
    """
    headers = {'X-CMC_PRO_API_KEY': app_id}
    try:
        r = requests.get('{}/cryptocurrency/map'.format(COINMARKETCAP_API_URL), headers=headers)
    except requests.exceptions.RequestException as e:
        sys.exit("Something went wrong: {}".format(e))
    if r.status_code != 200:
        sys.exit("Something went wrong with your call API: {}\n{}".format(r.status_code, r.json()))
    
    map_id = r.json()['data']
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
        return _get_rates(app_id, currency, namefile)
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
        r = requests.get('{}/fiat/map'.format(COINMARKETCAP_API_URL), headers=headers)
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
        return _get_fiat(api_key, currency, namefile)

def compute_holding(api_key, portfolio_filename, currency):
    """
    Compute the value of your portfolio given the quantity of each token owned

    :param api_key:            string,  the API key required to use the API
    :param portfolio_filename: string,  json file containing the info about your owned tokens
    :param currency:           string,  the currency wanted
    :return:                   dict,    value of each coins holded
    """
    try:
        portfolio = _load(portfolio_filename)
    except FileNotFoundError:
        sys.exit("No {} file found".format(portfolio_filename))

    slugs = ','.join(portfolio['data'][e]['slug'] for e in portfolio['data'])

    headers = {'X-CMC_PRO_API_KEY': api_key}
    payload = {'slug': slugs, 'convert': currency}

    try:
        r = requests.get('{}/cryptocurrency/quotes/latest'.format(COINMARKETCAP_API_URL), headers=headers, params=payload)
    except requests.exceptions.RequestException as e:
        sys.exit("Something went wrong: {}".format(e))
    if r.status_code != 200:
        sys.exit("Something went wrong with your call API: {}\n{}".format(r.status_code, r.json()))
    invested = portfolio['invested']['quantity']
    sum, res, quotes = 0, {}, r.json()['data']
    for cur in quotes:
        hold = portfolio['data'][quotes[cur]['symbol']]
        value = quotes[cur]['quote'][currency]['price'] * hold['quantity']
        sum += value
        res[quotes[cur]['symbol']] = {
            'price': quotes[cur]['quote'][currency]['price'],
            'quantity': hold['quantity'],
            'value': quotes[cur]['quote'][currency]['price'] * hold['quantity'],
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