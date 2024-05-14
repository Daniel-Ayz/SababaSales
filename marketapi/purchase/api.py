from typing import List

from marketapi import purchase
from ninja import Router

from ninja.security import django_auth

from .models import CustomUser, CustomPurchaseController, Cart, Basket, Product
from .schemas import (
    CustomPurchaseControllerSchema,
    CartSchema,
    BasketSchema,
    ProductSchema,
)


router = Router()


# -------------------- Get history --------------------
@router.get("/purchase/{purchase_id}", response=CustomPurchaseControllerSchema)
def get_purchase_history(request, user_id: int):
    try:
        user = CustomUser.objects.get(id=user_id)
        # not sure if this is the correct way to get all purchases of a user:
        purchase_history = user.purchasehistory_set.all()
        return 200, purchase_history
    except CustomUser.DoesNotExist as e:
        return 404, {"error": "User not found"}
    

# -------------------- Make Purchase --------------------

@router.post("/purchase/{cart_id}", response=CustomPurchaseControllerSchema)
def make_purchase_of_all_products_in_cart(request, user_id: int, cart_id: int):
    try:
        user = CustomUser.objects.get(id=user_id)
        cart = Cart.objects.get(id=cart_id)
        purchase = CustomPurchaseController.objects.create(user=user, cart=cart)
        for basket in cart.baskets.all():
            for basket_product in basket.basket_products.all():
                product = basket_product.product
                product.quantity -= basket_product.quantity
                product.save()
        return 200, purchase
    except CustomUser.DoesNotExist as e:
        return 404, {"error": "User not found"}
    except Cart.DoesNotExist as e:
        return 404, {"error": "Cart not found"}
    

@router.post("/purchase/{cart_id}/{product_id}", response=CustomPurchaseControllerSchema)
def cancel_purchase_of_entire_shopping_cart(request, user_id: int, cart_id: int):
    try:
        user = CustomUser.objects.get(id=user_id)
        cart = Cart.objects.get(id=cart_id)
        purchase = CustomPurchaseController.objects.get(user=user, cart=cart)
        purchase.delete()
        return 200, {"message": "Purchase has been canceled"}
    except CustomUser.DoesNotExist as e:
        return 404, {"error": "User not found"}
    except Cart.DoesNotExist as e:
        return 404, {"error": "Cart not found"}
    except CustomPurchaseController.DoesNotExist as e:
        return 404, {"error": "Purchase not found"}
    