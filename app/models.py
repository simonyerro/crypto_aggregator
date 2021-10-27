from typing import Optional
from pydantic import BaseModel

class token(BaseModel):
    slug: str
    quantity: float
    where: Optional[str] = None

# class portfolio(BaseModel):
#     invested: 


# {
#     "invested": {
#         "quantity": 11000,
#         "currency": "EUR"
#     },
#     "data":{
#         "ETH": {
#             "slug": "ethereum",    
#             "quantity": 0.7722,
#             "where": "Metamask"
#         },
#     }  
# }