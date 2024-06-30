from typing import List
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError

import store.api
import users.api

from ninja import Router

from store.schemas import PurchaseStoreProductSchema
from store.store_controller import StoreController

from purchase.schemas import HistoryBasketProductSchema
from users.models import Cart, CustomUser, Basket, BasketProduct
from purchase.models import HistoryBasket, HistoryBasketProduct, Purchase
from datetime import datetime

from purchase.adapters.payment_service import AbstractPaymentService
from purchase.adapters.delivery_service import (
    AbstractDeliveryService,
)  # Use actual delivery service when available

from users.usercontroller import UserController


router = Router()

sc = StoreController()
uc = UserController()


payment_service = AbstractPaymentService()
delivery_service = AbstractDeliveryService()


class purchaseController:

    # -------------------- Get history --------------------

    def get_purchase_history(self, request, user_id: int):
        try:
            purchase_history = []
            cart_ids = Cart.objects.filter(user_id=user_id).values_list("id", flat=True)
            purchase_ids = Purchase.objects.filter(cart_id__in=cart_ids).values_list(
                "purchase_id", flat=True
            )
            for purchase_id in purchase_ids:
                purchase_history.append(self.get_purchase_receipt(request, purchase_id))
            return purchase_history

        except CustomUser.DoesNotExist as e:
            raise HttpError(404, f'error": "User not found')
        except HttpError as e:
            raise e
        except Exception as e:
            raise HttpError(404, f'error": {str(e)}')

    # -------------------- Get purchase receipt --------------------
    def get_purchase_receipt(self, request, purchase_id: int):
        try:
            purchase = Purchase.objects.get(purchase_id=purchase_id)
            purchase_receipt = {
                "purchase_id": purchase.purchase_id,
                "purchase_date": purchase.purchase_date,
                "total_price": purchase.total_price,
                "total_quantity": purchase.total_quantity,
                "cart_id": purchase.cart.id,
                "baskets": [],
            }

            history_baskets = HistoryBasket.objects.filter(purchase=purchase)
            for history_basket in history_baskets:
                history_basket_schema = {
                    "basket_id": history_basket.basket_id,
                    "store_id": history_basket.store_id,
                    "total_price": history_basket.total_price,
                    "total_quantity": history_basket.total_quantity,
                    "discount": history_basket.discount,
                    "basket_products": [],
                }

                history_basket_products = HistoryBasketProduct.objects.filter(
                    history_basket=history_basket
                )
                for history_basket_product in history_basket_products:
                    history_basket_product_schema = {
                        "quantity": history_basket_product.quantity,
                        "name": history_basket_product.name,
                        "initial_price": history_basket_product.initial_price,
                    }
                    history_basket_schema["basket_products"].append(
                        history_basket_product_schema
                    )

                purchase_receipt["baskets"].append(history_basket_schema)
            return purchase_receipt

        except Purchase.DoesNotExist as e:
            raise HttpError(404, f'error": "Purchase not found')
        except HistoryBasket.DoesNotExist as e:
            raise HttpError(404, f'error": "HistoryBasket not found')
        except HistoryBasketProduct.DoesNotExist as e:
            raise HttpError(404, f'error": "HistoryBasketProduct not found')
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
        flag_delivery: bool = False,
        flag_payment: bool = False,
    ):
        try:
            # demo data
            if not flag_delivery:
                delivery_information_user = uc.get_user_delivery_information(
                    request, user_id
                )
                delivery_information_user["name"] = uc.get_user_full_name(
                    request, user_id
                )
            else:
                delivery_information_user = {
                    "address": "Maze Pinat Yaffo 10",
                    "city": "Tel Aviv",
                    "country": "Israel",
                    "zip": "1234567",
                }
                delivery_information_user["name"] = "Israel Israeli"
            if not flag_payment:
                payment_information_user = uc.get_user_payment_information(
                    request, user_id
                )
            else:
                payment_information_user = {
                    "currency": "USD",
                    "credit_card_number": "1234 5678 1234 5678",
                    "expiration_date": "12/23",
                    "security_code": "123",
                    "total_price": 0,
                    "holder": "Israel Israeli",
                    "holder_identification_number": "123456789",
                }

            payment_details = {
                "currency": payment_information_user["currency"],
                "credit_card_number": payment_information_user["credit_card_number"],
                "expiration_date": payment_information_user["expiration_date"],
                "security_code": payment_information_user["security_code"],
                "total_price": 0,
                "holder": uc.get_user_full_name(request, user_id),
                "holder_identification_number": uc.get_user_identification_number(
                    request, user_id
                ),
            }

            # if payment is ok:
            cart = get_object_or_404(Cart, id=cart_id)
            purchase = Purchase.objects.create(
                cart=cart, purchase_date=datetime.now(), total_price=0, total_quantity=0
            )
            total_price = 0
            total_quantity = 0
            item_counter = 0  # this is for the delivery service - idk why not
            for basket in Basket.objects.filter(cart_id=cart_id).values():
                store_id = basket["store_id"]
                products_list = []
                for product in BasketProduct.objects.filter(
                    basket_id=basket["id"]
                ).values():
                    name = product["name"]
                    quantity = product["quantity"]
                    category = product["category"]
                    schema = PurchaseStoreProductSchema(
                        product_name=name, quantity=quantity, category=category
                    )
                    products_list.append(schema)
                    item_counter += quantity
                try:
                    response = sc.purchase_product(
                        request=None, store_id=store_id, payload=products_list
                    )
                except HttpError as e:
                    Purchase.objects.filter(purchase_id=purchase.purchase_id).delete()
                    raise HttpError(400, str(e))

                # calculate total price and quantity per basket
                total_price += response["total_price"]
                total_basket_quantity = 0
                for basket_product in response["original_prices"]:
                    total_basket_quantity += basket_product["quantity"]

                total_quantity += total_basket_quantity
                history_basket = HistoryBasket.objects.create(
                    store_id=store_id,
                    purchase=purchase,
                    total_price=response["total_price"],
                    total_quantity=total_basket_quantity,
                    discount=response["original_price"] - response["total_price"],
                )
                history_basket.save()

                for basket_product_schema in response["original_prices"]:
                    history_basket_product = HistoryBasketProduct.objects.create(
                        quantity=basket_product_schema["quantity"],
                        name=basket_product_schema["name"],
                        initial_price=basket_product_schema["initial price"],
                        history_basket_id=history_basket.basket_id,
                    )
                    history_basket_product.save()

            delivery_result = delivery_service.create_shipment(
                delivery_information_user
            )

            if delivery_result["result"]:
                raise HttpError(400, f'error": "Delivery failed')

            total_price += delivery_result["delivery_fee"]

            payment_details["total_price"] = total_price
            payment_result = payment_service.process_payment(payment_details)
            if payment_result["result"]:
                raise HttpError(400, f'error": "Payment failed')
            Purchase.objects.filter(purchase_id=purchase.purchase_id).update(
                total_price=total_price, total_quantity=total_quantity
            )

            purchase = Purchase.objects.get(purchase_id=purchase.purchase_id)
            purchase.save()

            return {
                "message": "Purchase added successfully",
                "purchase_id": purchase.purchase_id,
                "purchase_date": purchase.purchase_date,
                "total_price": purchase.total_price,
                "total_quantity": purchase.total_quantity,
                "cart_id": purchase.cart_id,
            }

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
