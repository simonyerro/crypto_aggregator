# Crypto aggregator

The goal is to write a tool to aggregate the balances from your different wallet on multiple layer 1

In my case, I have **ETH** on metamask, **ADA** on Yoroi and **SOL** on Phantom

## Description

* The first step is to find API to do so. I can retrieve my ETH balance using api.blockchair.com
* I also use openexchangerates.org/api to convert the given balance to any traditional currency

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