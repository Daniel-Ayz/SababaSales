from ninja import Schema
from ninja.orm import ModelSchema

from .models import CustomPurchaseController, Cart, Basket, Product


# -------------------- Purchase --------------------


class CustomPurchaseControllerSchema(ModelSchema):
    class Meta:
        model = CustomPurchaseController
        fields = "__all__"


class CartSchema(ModelSchema):
    class Meta:
        model = Cart
        fields = "__all__"


class BasketSchema(ModelSchema):
    class Meta:
        model = Basket
        fields = "__all__"


class ProductSchema(ModelSchema):
    class Meta:
        model = Product
        fields = "__all__"