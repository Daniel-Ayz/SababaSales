from typing import List
from ninja import Schema
from ninja.orm import ModelSchema
from datetime import datetime

from .models import Purchase

# -------------------- Purchase --------------------


class PurchaseSchema(ModelSchema): # should be propbably changed
    class Meta:
        model = Purchase
        fields = "__all__"

class HistoryBasketProductSchema(Schema):
    quantity: int
    name: str
    initial_price: float

class HistoryBasketSchema(Schema):
    basket_id: int
    store_id: int
    total_price: float
    total_quantity: int
    discount: float
    basket_products: List[HistoryBasketProductSchema]

class PurchaseHistorySchema(Schema):
    purchase_id: int
    purchase_date: datetime
    total_price: float
    total_quantity: int
    cart_id: int
    baskets: List[HistoryBasketSchema]

class BidPurchaseHistorySchema(Schema):
    purchase_id: int
    bid_id: int
    purchase_date: datetime
    total_price: float
    total_quantity: int
    product_name: str