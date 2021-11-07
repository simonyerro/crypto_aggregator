"""
Pydantic models to validate the json file structure
"""

from typing import Optional, Dict
from pydantic import BaseModel

class Token(BaseModel):
    slug: str
    quantity: float
    where: Optional[str] = None

class Invested(BaseModel):
    quantity: float
    currency: str

class Portfolio(BaseModel):
    invested: Optional[Invested] = None
    data: Dict[str, Token]


# {
#     "invested": {
#         "quantity": 11000,
#         "currency": "EUR"
#     },
#     "data":[
#             {
#             "slug": "ethereum",    
#             "quantity": 0.7722,
#             "where": "Metamask"
#         },
#     ]
# }