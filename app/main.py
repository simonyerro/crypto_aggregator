from dotenv import load_dotenv
import helpers
import os
import uuid
import secrets

from fastapi import FastAPI, Depends, HTTPException 
import firebase_admin
from google.cloud import firestore

firebase_admin.initialize_app()
db = firestore.Client()
load_dotenv()

app = FastAPI()
load_dotenv()
coinmarketcap_api_key = os.getenv('COINMARKETCAP_API')

def auth(api_key):
    user = db.collection(u'users').document(api_key).get()
    if user.exists:
        return user
    else:
        raise HTTPException(
            status_code=403, detail="Could not validate credentials"
        ) 


@app.get('/portfolio')
def get_portfolio_value(api_key: str = Depends(auth)):
    return helpers.compute_holding(coinmarketcap_api_key, '../files/portfolio.json', 'EUR')

@app.get('/signin')
def authenticate():
    api_key = secrets.token_urlsafe(64)
    db.collection(u'users').document(api_key).set({})
    return {
        'token': api_key,
        'message': 'save_this_carefully'
    }

# @app.put("/portolio")
# def put_portfolio(portfolio: ):
#     return {"item_name": item.name, "item_id": item_id}