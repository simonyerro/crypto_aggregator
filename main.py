from dotenv import load_dotenv
import helpers
import os

load_dotenv()
coinmarketcap_api_key = os.getenv('COINMARKETCAP_API')

if __name__ == "__main__":
    print(helpers.compute_holding(coinmarketcap_api_key, 'portfolio.json', 'EUR'))