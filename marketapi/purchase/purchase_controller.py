from typing import List

from purchase.schemas import PurchaseSchema

from ninja import Router


from users.models import Cart, CustomUser, Basket, BasketProduct
from purchase.models import Purchase
from datetime import datetime

from purchase.adapters.payment_service import AbstractPaymentService
from purchase.adapters.delivery_service import (
    AbstractDeliveryService,
)  # Use actual delivery service when available

router = Router()

payment_service = AbstractPaymentService()
delivery_service = (
    AbstractDeliveryService()
)  # Replace with RealDeliveryService when available


class purchaseController:

    # -------------------- Get history --------------------

    @router.get("/purchase/{user_id}/get_purchase_history", response=PurchaseSchema)
    def get_purchase_history(request, user_id: int):
        try:

            cart_ids = Cart.objects.filter(user_id=user_id).values_list('cart_id', flat=True)
            purchase_history = Purchase.objects.filter(cart_id__in=cart_ids)
            
            return 200, purchase_history
        
        except CustomUser.DoesNotExist as e:
            return 404, {"error": "User not found"}
        

    # -------------------- Make Purchase --------------------

    # check
    @router.post("/purchase/{cart_id}/make_purchase", response=PurchaseSchema)
    def make_purchase(request, cart_id: int):
        try:
            # integrate delivery service and payment service
            # TODO: somehow get address - probably from user facade
            # TODO: same about package details
            address = "Test address"
            package_details = "Test package details"
            payment_method = {"service": "paypal", "currency": "USD", "amount": 100.0, "billing_address": "Test billing address"}

            delivery_result = delivery_service.create_shipment(address, package_details)
            # if delivery is ok:
            # TODO: somehow get payment method - probably from user facade, or even argument
            payment_result = payment_service.process_payment(payment_method)
            # if payment is ok:


            purchase = Purchase.objects.create(cart_id = cart_id, 
                                               purchase_date = datetime.now())
            

            for basket in Basket.objects.filter(cart_id = cart_id).values():
                store_id = basket['store_id']
                products_list = []
                for product in BasketProduct.objects.filter(basket_id = basket.id).values():
                    name = product['name']
                    quantity = product['quantity']
                    products_list.append((name, quantity))

                store.models.api.purchase_product(store_id, products_list)

            purchase.save()
            return 200, purchase
        
        except CustomUser.DoesNotExist as e:
            return 404, {"error": "User not found"}
        except Cart.DoesNotExist as e:
            return 404, {"error": "Cart not found"}
        except Basket.DoesNotExist as e:
            return 404, {"error": "Basket not found"}
        except BasketProduct.DoesNotExist as e:
            return 404, {"error": "BasketProduct not found"}
        except Exception as e:
            return 404, {"error": str(e)}