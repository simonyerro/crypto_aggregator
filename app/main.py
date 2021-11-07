"""
Run the app
"""

import os
import secrets
import json
from dotenv import load_dotenv
import helpers

from models import Portfolio

from fastapi import FastAPI, Depends, HTTPException, Request
import firebase_admin
from google.cloud import firestore

firebase_admin.initialize_app()
db = firestore.Client()
load_dotenv()

app = FastAPI()
load_dotenv()
coinmarketcap_api_key = os.getenv('COINMARKETCAP_API')

def auth(api_key):
    user = db.collection('users').document(api_key).get()
    if user.exists:
        return user
    raise HTTPException(
        status_code=403, detail="Could not validate credentials"
    )

@app.get('/signin')
def authenticate():
    api_key = secrets.token_urlsafe(64)
    db.collection('users').document(api_key).set({})
    return {
        'token': api_key,
        'message': 'save_this_carefully'
    }

@app.get('/portfolio', dependencies = [Depends(auth)])
def get_portfolio_value(request: Request):
    api_key = request.query_params['api_key']
    portfolio = db.collection('portfolio').document(api_key).get()
    print(portfolio)
    if portfolio.exists:
        return helpers.compute_holding(coinmarketcap_api_key, portfolio.to_dict(), 'EUR')
    raise HTTPException(
        status_code=403, detail="Could not validate credentials"
    )

@app.put("/portfolio", dependencies = [Depends(auth)])
def put_portfolio(portfolio: Portfolio, request: Request):
    api_key = request.query_params['api_key']
    db.collection('portfolio').document(api_key).set(portfolio.dict())
    return portfolio
