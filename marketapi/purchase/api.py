from typing import List

from marketapi import purchase
from ninja import Router

from ninja.security import django_auth

from django.shortcuts import get_object_or_404, aget_object_or_404

from .models import CustomUser, PurchaseController, Cart, Basket, Product
from .schemas import (
    PurchaseControllerSchema,
    CartSchema,
    BasketSchema,
    ProductSchema,
)
from purchase.adapters.payment_service import AbstractPaymentService
from purchase.adapters.delivery_service import (
    AbstractDeliveryService,
)  # Use actual delivery service when available


router = Router()

payment_service = AbstractPaymentService()
delivery_service = (
    AbstractDeliveryService()
)  # Replace with RealDeliveryService when available


# -------------------- Get history --------------------
@router.get("/purchase/{purchase_id}", response=PurchaseControllerSchema)
def get_purchase_history(request, user_id: int):
    try:
        purchase_history = PurchaseController.objects.filter(user_id=user_id)
        return 200, purchase_history
    except CustomUser.DoesNotExist as e:
        return 404, {"error": "User not found"}


# -------------------- Make Purchase --------------------


@router.post("/purchase/{cart_id}", response=PurchaseControllerSchema)
def make_purchase_of_all_products_in_cart(request, user_id: int, cart_id: int):
    try:
        cart = get_object_or_404(Cart, pk=cart_id)

        # integrate delivery service and payment service
        # TODO: somehow get address - probably from user facade
        # TODO: same about package details
        delivery_result = delivery_service.create_shipment(address, package_details)
        # if delivery is ok:
        # TODO: somehow get payment method - probably from user facade, or even argument
        payment_result = payment_service.process_payment(payment_method)
        # if payment is ok:

        purchase = PurchaseController.objects.create(user_id=user_id, cart=cart)
        for basket in cart.baskets.all():
            for product in basket.products.all():
                # stores has function: def purchase_product(request, store_id: int, payload: List[PurchaseStoreProductSchema]):
                purchase_product(basket.store_id, [product])
        return 200, purchase
    except CustomUser.DoesNotExist as e:
        return 404, {"error": "User not found"}
    except Cart.DoesNotExist as e:
        return 404, {"error": "Cart not found"}


# this function seems to be unnecessary because Stores has this functionality in purchase_product


@router.post("/purchase/{cart_id}/{product_id}", response=PurchaseControllerSchema)
def cancel_purchase_of_entire_shopping_cart(request, user_id: int, cart_id: int):
    try:
        cart = get_object_or_404(Cart, pk=cart_id)
        purchase = PurchaseController.objects.get(user_id=user_id, cart=cart)
        purchase.delete()
        return 200, {"message": "Purchase has been canceled"}
    except CustomUser.DoesNotExist as e:
        return 404, {"error": "User not found"}
    except Cart.DoesNotExist as e:
        return 404, {"error": "Cart not found"}
    except PurchaseController.DoesNotExist as e:
        return 404, {"error": "Purchase not found"}
