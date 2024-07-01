from typing import List

from ninja import Router

from django.contrib.auth import login as django_login
from ninja.security import django_auth

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


@router.post("/fake_data")
def create_fake_data(request):
    return uc.create_fake_data()


# get user id by email
@router.get("/get_user_id", response={200: UserSchema, 404: Error})
def get_user_id(request, email: str):
    return uc.get_user_id(request, email)


@router.post("/{user_id}/update_Full_Name")
def update_user_full_name(request, user_id, payload: FullnameSchemaIn):
    return uc.update_user_full_name(request, user_id, payload)


@router.post("/{user_id}/update_Identification_Number")
def update_user_Identification_Number(
    request, user_id, payload: IdentificationNumberSchemaIn
):
    return uc.update_user_Identification_Number(request, user_id, payload)


@router.post("/{user_id}/update_delivery_info")
def update_user_delivery_info(request, user_id, payload: DeliveryInfoSchema):
    return uc.update_user_delivery_info(request, user_id, payload)


@router.post("/{user_id}/update_payment_info")
def update_user_payment_info(request, user_id, payload: PaymentInfoSchema):
    return uc.update_user_payment_info(request, user_id, payload)


@router.get("/{user_id}/get_payment_information")
def get_payment_information(request, user_id):
    return uc.get_payment_information(request, user_id)


@router.get("/{user_id}/get_delivery_information")
def get_delivery_information(request, user_id):
    return uc.get_delivery_information(request, user_id)


@router.get("/{user_id}/get_full_name")
def get_full_name(request, user_id):
    return uc.get_user_full_name(request, user_id)
