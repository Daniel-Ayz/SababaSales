from typing import List
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError

import store.api
import users.api

from ninja import Router

from store.schemas import PurchaseStoreProductSchema
from store.store_controller import StoreController

from users.models import Cart, CustomUser, Basket, BasketProduct
from purchase.models import Purchase
from datetime import datetime

from purchase.adapters.payment_service import AbstractPaymentService
from purchase.adapters.delivery_service import (
    AbstractDeliveryService,
)  # Use actual delivery service when available

# from users.usercontroller import UserController


router = Router()

sc = StoreController()
# uc = UserController()


payment_service = AbstractPaymentService()
delivery_service = AbstractDeliveryService()


class purchaseController:

    # -------------------- Get history --------------------

    def get_purchase_history(self, request, user_id: int):
        try:
            cart_ids = Cart.objects.filter(user_id=user_id).values_list("id", flat=True)
            purchase_history = Purchase.objects.filter(cart_id__in=cart_ids)

            return purchase_history

        except CustomUser.DoesNotExist as e:
            raise HttpError(404, f'error": "User not found')
        except HttpError as e:
            raise e
        except Exception as e:
            raise HttpError(404, f'error": {str(e)}')

    # -------------------- Make Purchase --------------------

    def make_purchase(
        self,
        request,
        user_id: int,  # the user that purchases this cart
        cart_id: int,
        flag_delivery: bool = True,
        flag_payment: bool = True,
    ):
        try:
            # demo data
            address = "Test address"
            package_details = "Test package details"
            payment_method = {
                "service": "paypal",
                "currency": "USD",
                "billing_address": "Test billing address",
            }
            # TODO: add this functionality to user facade
            # address = uc.get_user_address(user_id)
            # payment_information_user = uc.get_user_payment_information(user_id)

            # payment_method = payment_information_user["service"]
            # currency = payment_information_user["currency"]
            # billing_address = payment_information_user["billing_address"]

            # if payment is ok:
            cart = get_object_or_404(Cart, id=cart_id)

            purchase = Purchase.objects.create(cart=cart, purchase_date=datetime.now())

            for basket in Basket.objects.filter(cart_id=cart_id).values():
                store_id = basket["store_id"]
                products_list = []
                for product in BasketProduct.objects.filter(
                    basket_id=basket["id"]
                ).values():
                    name = product["name"]
                    quantity = product["quantity"]
                    schema = PurchaseStoreProductSchema(
                        product_name=name, quantity=quantity
                    )
                    products_list.append(schema)

                amount = sc.purchase_product(
                    request=None, store_id=store_id, payload=products_list
                )["total_price"]

            delivery_result = delivery_service.create_shipment(
                address, package_details, flag_delivery
            )

            if delivery_result["result"]:
                raise HttpError(400, f'error": "Delivery failed')
            amount += delivery_result["delivery_fee"]

            payment_method["amount"] = amount
            payment_result = payment_service.process_payment(
                payment_method, flag_payment
            )
            if payment_result["result"]:
                raise HttpError(400, f'error": "Payment failed')

            purchase.save()
            return {"message": "Purchase added successfully"}

        except CustomUser.DoesNotExist as e:
            raise HttpError(404, f'error": "User not found')
        except Cart.DoesNotExist as e:
            raise HttpError(404, f'error": "Cart not found')
        except Basket.DoesNotExist as e:
            raise HttpError(404, f'error": "Basket not found')
        except BasketProduct.DoesNotExist as e:
            raise HttpError(404, f'error": "BasketProduct not found')
        except HttpError as e:
            raise e
        except Exception as e:
            raise HttpError(404, f'error": {str(e)}')
