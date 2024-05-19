from typing import List

from ninja import Schema
from ninja.orm import ModelSchema

from .models import CustomUser, Notification, Cart, Basket, BasketProduct


# -------------------- AUTH --------------------


class UserRegisterSchema(Schema):
    username: str
    email: str
    password: str


class UserLoginSchema(Schema):
    username: str
    password: str


class Error(Schema):
    error: str


class Msg(Schema):
    msg: str


# -------------------- User --------------------


class UserSchema(ModelSchema):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email"]


class NotificationIn(Schema):
    msg: str


class NotificationSchema(ModelSchema):
    # user: UserSchema
    class Meta:
        model = Notification
        exclude = ["user"]


class BasketProductSchema(ModelSchema):
    class Meta:
        model = BasketProduct
        exclude = ["id", "basket"]


class BasketSchema(Schema):
    id: int
    store_id: int
    basket_products: List[BasketProductSchema]


class CartSchema(Schema):
    user: UserSchema
    baskets: List[BasketSchema]


class StoreProduct(BasketProductSchema):
    store_id: int
