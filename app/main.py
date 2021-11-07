"""
Run the app
"""

import os
import secrets
from dotenv import load_dotenv
import helpers

from models import Portfolio

from fastapi import FastAPI, Depends, HTTPException, Request
from firebase_admin import initialize_app, auth
from google.cloud import firestore

initialize_app()
db = firestore.Client()
load_dotenv()

app = FastAPI()
load_dotenv()
coinmarketcap_api_key = os.getenv('COINMARKETCAP_API')
firebase_api_key = os.getenv('FIREBASE_API_KEY')

def authenticate(api_key):
    user = db.collection('users').document(api_key).get()
    if user.exists:
        return user
    raise HTTPException(
        status_code=403, detail="Could not validate credentials"
    )

@app.get('/signin')
def signin():
    api_key = secrets.token_urlsafe(64)
    db.collection('users').document(api_key).set({})
    return {
        'token': api_key,
        'message': 'save_this_carefully'
    }

@app.get('/portfolio', dependencies = [Depends(authenticate)])
def get_portfolio_value(request: Request):
    api_key = request.query_params['api_key']
    portfolio = db.collection('portfolio').document(api_key).get()
    print(portfolio)
    if portfolio.exists:
        return helpers.compute_holding(coinmarketcap_api_key, portfolio.to_dict(), 'EUR')
    raise HTTPException(
        status_code=403, detail="Could not validate credentials"
    )

@app.put("/portfolio", dependencies = [Depends(authenticate)])
def put_portfolio(portfolio: Portfolio, request: Request):
    api_key = request.query_params['api_key']
    db.collection('portfolio').document(api_key).set(portfolio.dict())
    return portfolio
