from typing import List

from ninja import Router

from django.contrib.auth import authenticate, login as django_login
from django.contrib.auth.hashers import make_password
from ninja.security import django_auth

from .models import CustomUser, Notification, Cart, Basket, BasketProduct
from .schemas import (
    UserRegisterSchema,
    UserLoginSchema,
    UserSchema,
    Error,
    NotificationSchema,
    CartSchema,
    BasketSchema,
    BasketProductSchema,
)


router = Router()


# -------------------- AUTH --------------------


@router.post("/register", response={200: UserSchema, 400: Error})
def register(request, payload: UserRegisterSchema):
    # Hash the password before saving
    payload.password = make_password(payload.password)
    user = CustomUser.objects.create(
        username=payload.username, email=payload.email, password=payload.password
    )
    user.save()
    return {"id": user.id, "username": user.username, "email": user.email}


@router.post("/login", response={200: UserSchema, 401: Error})
def login(request, payload: UserLoginSchema):
    user = authenticate(request, username=payload.username, password=payload.password)
    if user:
        django_login(request, user)
        return 200, {"id": user.id, "username": user.username, "email": user.email}
    else:
        return 401, {"error": "Invalid credentials"}


@router.get("/secret", auth=django_auth)
def secret(request):
    return {"message": "You are authenticated"}


# -------------------- Get --------------------


@router.get("/users", response={200: List[UserSchema]})
def get_users(request):
    users = CustomUser.objects.all()
    return 200, users


@router.get("/users/{int:user_id}", response={200: UserSchema, 404: Error})
def get_user(request, user_id: int):
    try:
        user = CustomUser.objects.get(id=user_id)
        return 200, user
    except CustomUser.DoesNotExist as e:
        return 404, {"error": "User not found"}


@router.delete("/users/{int:user_id}", response={204: None, 404: Error})
def delete_user(request, user_id: int):
    try:
        user = CustomUser.objects.get(id=user_id)
        user.delete()
        return 204, None
    except CustomUser.DoesNotExist as e:
        return 404, {"error": "User not found"}


@router.put("/users/{int:user_id}", response={200: UserSchema, 404: Error})
def update_user(request, user_id: int, payload: UserRegisterSchema):
    try:
        user = CustomUser.objects.get(id=user_id)
        user.username = payload.username
        user.email = payload.email
        user.password = make_password(payload.password)
        user.save()
        return 200, user
    except CustomUser.DoesNotExist as e:
        return 404, {"error": "User not found"}


@router.get(
    "/users/{int:user_id}/notifications",
    response={200: List[NotificationSchema], 404: Error},
)
def get_user_notifications(request, user_id: int):
    try:
        user = CustomUser.objects.get(id=user_id)
        notifications = user.notification_set.all()
        return 200, notifications
    except CustomUser.DoesNotExist as e:
        return 404, {"error": "User not found"}


@router.get("/users/{int:user_id}/cart", response={200: CartSchema, 404: Error})
def get_user_cart(request, user_id: int):
    try:
        user = CustomUser.objects.get(id=user_id)
        cart = user.cart
        return 200, cart
    except CustomUser.DoesNotExist as e:
        return 404, {"error": "User not found"}


@router.get(
    "/users/{int:user_id}/cart/basket", response={200: List[BasketSchema], 404: Error}
)
def get_user_basket(request, user_id: int):
    try:
        user = CustomUser.objects.get(id=user_id)
        cart = user.cart
        baskets = cart.basket_set.all()
        return 200, baskets
    except CustomUser.DoesNotExist as e:
        return 404, {"error": "User not found"}


@router.get(
    "/users/{int:user_id}/cart/basket/{int:basket_id}",
    response={200: BasketSchema, 404: Error},
)
def get_user_basket(request, user_id: int, basket_id: int):
    try:
        user = CustomUser.objects.get(id=user_id)
        cart = user.cart
        basket = cart.basket_set.get(id=basket_id)
        return 200, basket
    except CustomUser.DoesNotExist as e:
        return 404, {"error": "User not found"}
    except Basket.DoesNotExist as e:
        return 404, {"error": "Basket not found"}


@router.get(
    "/users/{int:user_id}/cart/basket/{int:basket_id}/products",
    response={200: List[BasketProductSchema], 404: Error},
)
def get_user_basket_products(request, user_id: int, basket_id: int):
    try:
        user = CustomUser.objects.get(id=user_id)
        cart = user.cart
        basket = cart.basket_set.get(id=basket_id)
        products = basket.basketproduct_set.all()
        return 200, products
    except CustomUser.DoesNotExist as e:
        return 404, {"error": "User not found"}
    except Basket.DoesNotExist as e:
        return 404, {"error": "Basket not found"}


@router.get(
    "/users/{int:user_id}/cart/basket/{int:basket_id}/products/{int:product_id}",
    response={200: BasketProductSchema, 404: Error},
)
def get_user_basket_product(request, user_id: int, basket_id: int, product_id: int):
    try:
        user = CustomUser.objects.get(id=user_id)
        cart = user.cart
        basket = cart.basket_set.get(id=basket_id)
        product = basket.basketproduct_set.get(id=product_id)
        return 200, product
    except CustomUser.DoesNotExist as e:
        return 404, {"error": "User not found"}
    except Basket.DoesNotExist as e:
        return 404, {"error": "Basket not found"}
    except BasketProduct.DoesNotExist as e:
        return 404, {"error": "Product not found"}


@router.post(
    "/users/{int:user_id}/cart/basket/{int:basket_id}/products",
    response={200: BasketProductSchema, 404: Error},
)
def add_user_basket_product(
    request, user_id: int, basket_id: int, payload: BasketProductSchema
):
    try:
        user = CustomUser.objects.get(id=user_id)
        cart = user.cart
        basket = cart.basket_set.get(id=basket_id)
        product = basket.basketproduct_set.create(
            id=payload.id, quantity=payload.quantity
        )
        product.save()
        return 200, product
    except CustomUser.DoesNotExist as e:
        return 404, {"error": "User not found"}
    except Basket.DoesNotExist as e:
        return 404, {"error": "Basket not found"}


# -------------------- Create --------------------


@router.post(
    "/users/{int:user_id}/notifications", response={200: NotificationSchema, 404: Error}
)
def add_user_notification(request, user_id: int, payload: NotificationSchema):
    try:
        user = CustomUser.objects.get(id=user_id)
        notification = user.notification_set.create(
            sent_by=payload.sent_by, message=payload.message, seen=payload.seen
        )
        notification.save()
        return 200, notification
    except CustomUser.DoesNotExist as e:
        return 404, {"error": "User not found"}


@router.post("/users/{int:user_id}/cart", response={200: CartSchema, 404: Error})
def add_user_cart(request, user_id: int):
    try:
        user = CustomUser.objects.get(id=user_id)
        cart = user.cart_set.create(user=user)
        cart.save()
        return 200, cart
    except CustomUser.DoesNotExist as e:
        return 404, {"error": "User not found"}


@router.post(
    "/users/{int:user_id}/cart/basket", response={200: BasketSchema, 404: Error}
)
def add_user_basket(request, user_id: int, payload: BasketSchema):
    try:
        user = CustomUser.objects.get(id=user_id)
        cart = user.cart
        basket = cart.basket_set.create(store_id=payload.store_id)
        basket.save()
        return 200, basket
    except CustomUser.DoesNotExist as e:
        return 404, {"error": "User not found"}


@router.post(
    "/users/{int:user_id}/cart/basket/{int:basket_id}/products",
    response={200: BasketProductSchema, 404: Error},
)
def add_user_basket_product(
    request, user_id: int, basket_id: int, payload: BasketProductSchema
):
    try:
        user = CustomUser.objects.get(id=user_id)
        cart = user.cart
        basket = cart.basket_set.get(id=basket_id)
        product = basket.basketproduct_set.create(
            id=payload.id, quantity=payload.quantity
        )
        product.save()
        return 200, product
    except CustomUser.DoesNotExist as e:
        return 404, {"error": "User not found"}
    except Basket.DoesNotExist as e:
        return 404, {"error": "Basket not found"}


# -------------------- Update --------------------
