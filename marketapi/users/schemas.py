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


# -------------------- User --------------------


class UserSchema(ModelSchema):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email"]


class NotificationSchema(Schema):
    class Meta:
        model = Notification
        fields = "__all__"


class CartSchema(ModelSchema):
    class Meta:
        model = Cart
        fields = "__all__"


class BasketSchema(ModelSchema):
    class Meta:
        model = Basket
        fields = "__all__"


class BasketProductSchema(ModelSchema):
    class Meta:
        model = BasketProduct
        fields = "__all__"
