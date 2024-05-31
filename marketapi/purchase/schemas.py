from ninja import Schema
from ninja.orm import ModelSchema

from .models import Purchase

# -------------------- Purchase --------------------


class PurchaseSchema(ModelSchema): # should be propbably changed
    class Meta:
        model = Purchase
        fields = "__all__"

class HistoryBasketProductSchema(Schema):
    product_name: str
    quantity: int
    initial_price: float
