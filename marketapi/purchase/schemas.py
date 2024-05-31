from ninja import Schema
from ninja.orm import ModelSchema

from .models import Purchase

# -------------------- Purchase --------------------


class PurchaseSchema(ModelSchema):
    class Meta:
        model = Purchase
        fields = "__all__"

class HistoryBasketProductSchema(Schema):
    product_name: str
    quantity: int
    initial_price: float
    post_discount_price: float