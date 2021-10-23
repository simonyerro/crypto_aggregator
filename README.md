# Crypto aggregator (This README is not up-to-date)

The goal is to write a tool to aggregate the balances from your different wallet on multiple layer 1

In my case, I have **ETH** on metamask, **ADA** on Yoroi and **SOL** and other layers 2 on Phantom, additional crypto on Binance...

## Description

There are currently two distinct tools written:

* **get_eth_wallet_balance**, A function to get the balance of an ETH address in any currency wanted
* **compute_holding**, A function to get the value of your total portfolio providing a portfolio.json file with the quantity of each token (You can take a look at example_portfolio.json).

    Since I don't buy very often, I thought this would do the work for now

## How to use 

You need to provide an API key for the openexchangerates API and your ETH address
You can provide a .env file looking like this:
```bash
ETHEREUM_ADDRESS="0xY0UR3TH3R3UM4DDR3355"
OPENEXCHANGERATES_APP_ID="your_api_id"
```

and source it with:
```bash
source .env
```

You can directly use the script running:

```bash
python3 get_ethereum_balance.py
```

## License
Copyright (c) We Are Interactive under the MIT license.