# Crypto aggregator

The goal is to write a tool to aggregate the balances from your different wallet on multiple layer 1

In my case, I have **ETH** on metamask, **ADA** on Yoroi and **SOL** and other layers 2 on Phantom, additional crypto on Binance...

## Description

## How to use

You need to provide API keys for the CoinmarketCap API, Firebase and GCP service account
You can provide a .env file looking like this:

```bash
export COINMARKETCAP_API='secret_key'
export GOOGLE_APPLICATION_CREDENTIALS='secret/path/to/file.json'
export FIREBASE_API_KEY='secret_key'
```

and source it with:

```bash
source .env
```

Install the dependencies with:

```bash
poetry install
```

You can then launch the backend with:

```bash
poetry shell
uvicorn main:app --reload #This is currently not ready for production
```

## Endpoints

You can access the doc on `http://localhost:8000/docs`

## License

Copyright (c) We Are Interactive under the MIT license.
