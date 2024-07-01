from typing import List

from ninja import Schema
from ninja.orm import ModelSchema
from typing import Optional

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


class UserSetupSchema(Schema):

    id: int  #
    username: str  #
    email: str  #
    cart_id: int


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


class BasketProductSchemaOut(ModelSchema):
    class Meta:
        model = BasketProduct
        exclude = ["basket"]


class BasketSchema(Schema):
    id: int
    store_id: int
    basket_products: List[BasketProductSchemaOut]


class CartSchema(Schema):
    user: UserSchema
    baskets: List[BasketSchema]


class StoreProduct(BasketProductSchema):
    store_id: int


class DeliveryInfoSchema(Schema):
    address: str
    city: str
    country: str
    zip: str


class PaymentInfoSchema(Schema):
    holder: str
    holder_identification_number: str
    currency: str
    credit_card_number: str
    expiration_date: str
    security_code: str
