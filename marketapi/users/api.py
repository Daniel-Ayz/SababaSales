from typing import List
import time

from ninja import Router

from django.contrib.auth import authenticate, login as django_login
from django.contrib.auth.hashers import make_password
from ninja.security import django_auth

from .models import CustomUser, Notification, Cart, Basket, BasketProduct

# from .schemas import (
#     UserRegisterSchema,
#     UserLoginSchema,
#     UserSchema,
#     Error,
#     NotificationSchema,
#     CartSchema,
#     BasketSchema,
#     BasketProductSchema,
# )
from .schemas import *
from .usercontroller import UserController

router = Router()
uc = UserController()


# -------------------- AUTH --------------------


@router.post("/register", response={200: UserSchema, 401: Error})
def register(request, payload: UserRegisterSchema):
    user = uc.register(request, payload)
    return user


@router.post("/login", response={200: UserSchema, 401: Error})
def login(request, payload: UserLoginSchema):
    user = uc.login(request, payload)
    return user


@router.post("/logout", response={200: Msg})
def logout(request):
    return uc.logout(request)


@router.get("/", response={200: UserSetupSchema, 401: Error}, auth=django_auth)
def get_user(request):
    user = uc.get_user(request)
    return user


# # user must be authenticated to get their own user info
# @router.get("/{int:user_id}", response={200: UserSchema}, auth=django_auth)
# def get_user(request, user_id: int):
#     return uc.get_user(request, user_id)


@router.delete("/{int:user_id}", response={200: Msg, 401: Error})
def delete_user(request, user_id: int):
    return uc.delete_user(request, user_id)


# user must be authenticated to update their own user info
@router.put("/{int:user_id}", response={200: UserSchema, 404: Error}, auth=django_auth)
def update_user(request, user_id: int, payload: UserRegisterSchema):
    return uc.update_user(request, user_id, payload)


# only a logged
@router.get(
    "/users/notifications",
    response={200: List[NotificationSchema], 404: Error},
)
def get_user_notifications(request):
    return uc.get_user_notifications(request)


# send notifications for other user
@router.post(
    "/notifications/{int:target_user_id}",
    response={200: NotificationSchema, 404: Error},
)
def send_notification(request, target_user_id: int, payload: NotificationIn):
    return uc._send_notification(request, target_user_id, payload)


@router.put(
    "/notifications/{int:notification_id}/",
    response={200: NotificationSchema, 404: Error},
)
def mark_notification_as_seen(request, notification_id: int):
    return uc.mark_notification_as_seen(request, notification_id)


@router.get("/cart", response={200: CartSchema, 404: Error})
def get_user_cart(request):
    """
    returns the cart of the current session user(all baskets)
    """
    return uc.get_user_cart(request)


@router.get("/cart/basket{int:basket_id}", response={200: BasketSchema, 404: Error})
def get_user_basket(request, basket_id: int):
    """
    returns  basket of the current session user, with the given id
    """
    return uc.get_user_basket(request, basket_id)


@router.get("/cart/products", response={200: List[BasketProductSchema], 404: Error})
def get_user_products(request):
    """
    returns the products of the current session user
    """
    return uc.get_user_products(request)


@router.delete("/cart/{int:productId}", response={200: Msg, 404: Error})
def delete_user_cart_product(request, productId: int):
    """
    deletes a product from the current session user cart
    """
    return uc.delete_user_cart_product(request, productId)


@router.post("/cart/products", response={200: BasketProductSchema, 404: Error})
def add_user_product(request, payload: StoreProduct):
    """
    adds a product to the current session user
    this function is the only way to create a basket for a user, as the basket is created when the first product is added
    """
    return uc.add_basket_product(request, payload)


# @router.get("/time")
# def test_time(request):
#     time.sleep(10)
#     return {"msg" "waited!"}
#
#
# @router.post(
#     "/users/{int:user_id}/notifications", response={200: NotificationSchema, 404: Error}
# )
# def add_user_notification(request, user_id: int, payload: NotificationSchema):
#     try:
#         user = CustomUser.objects.get(id=user_id)
#         notification = user.notification_set.create(
#             sent_by=payload.sent_by, message=payload.message, seen=payload.seen
#         )
#         notification.save()
#         return 200, notification
#     except CustomUser.DoesNotExist as e:
#         return 404, {"error": "User not found"}
#
#
# @router.post("/users/{int:user_id}/cart", response={200: CartSchema, 404: Error})
# def add_user_cart(request, user_id: int):
#     try:
#         user = CustomUser.objects.get(id=user_id)
#         cart = user.cart_set.create(user=user)
#         cart.save()
#         return 200, cart
#     except CustomUser.DoesNotExist as e:
#         return 404, {"error": "User not found"}
#
#
# @router.post(
#     "/users/{int:user_id}/cart/basket", response={200: BasketSchema, 404: Error}
# )
# def add_user_basket(request, user_id: int, payload: BasketSchema):
#     try:
#         user = CustomUser.objects.get(id=user_id)
#         cart = user.cart
#         basket = cart.basket_set.create(store_id=payload.store_id)
#         basket.save()
#         return 200, basket
#     except CustomUser.DoesNotExist as e:
#         return 404, {"error": "User not found"}
#
#
# @router.post(
#     "/users/{int:user_id}/cart/basket/{int:basket_id}/products",
#     response={200: BasketProductSchema, 404: Error},
# )
# def add_user_basket_product(
#         request, user_id: int, basket_id: int, payload: BasketProductSchema
# ):
#     try:
#         user = CustomUser.objects.get(id=user_id)
#         cart = user.cart
#         basket = cart.basket_set.get(id=basket_id)
#         product = basket.basketproduct_set.create(
#             id=payload.id, quantity=payload.quantity
#         )
#         product.save()
#         return 200, product
#     except CustomUser.DoesNotExist as e:
#         return 404, {"error": "User not found"}
#     except Basket.DoesNotExist as e:
#         return 404, {"error": "Basket not found"}
#
# -------------------- Update --------------------
@router.post("/fake_data")
def create_fake_data(request):
    return uc.create_fake_data()


# get user id by email
@router.get("/get_user_id", response={200: UserSchema, 404: Error})
def get_user_id(request, email: str):
    return uc.get_user_id(request, email)
