from typing import List
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError

from ninja import Router

from store.schemas import PurchaseStoreProductSchema
from store.store_controller import StoreController

from purchase.schemas import HistoryBasketProductSchema
from users.models import Cart, CustomUser, Basket, BasketProduct
from purchase.models import HistoryBasket, HistoryBasketProduct, Purchase
from datetime import datetime

from purchase.services.payment_service import AbstractPaymentService
from purchase.services.delivery_service import (
    AbstractDeliveryService,
)  # Use actual delivery service when available

from users.usercontroller import UserController
from django.db import transaction


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
            raise HttpError(404, "User not found")
        except HttpError as e:
            raise e
        except Exception as e:
            raise HttpError(404, f"{str(e)}")

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
            raise HttpError(404, "Purchase not found")
        except HistoryBasket.DoesNotExist as e:
            raise HttpError(404, "HistoryBasket not found")
        except HistoryBasketProduct.DoesNotExist as e:
            raise HttpError(404, "HistoryBasketProduct not found")
        except HttpError as e:
            raise e
        except Exception as e:
            raise HttpError(404, f"{str(e)}")

    # -------------------- Make Purchase --------------------

    def make_purchase(
        self,
        request,
        user_id: int,  # the user that purchases this cart
        cart_id: int,
    ):
        try:
            delivery_information_dict = self.get_delivery_info_dict(request, user_id)
            
            payment_details_dict = self.get_payment_info_dict(request, user_id)

            with transaction.atomic():
                cart = get_object_or_404(Cart, id=cart_id)
                purchase = Purchase.objects.create(
                    cart=cart,
                    purchase_date=datetime.now(),
                    total_price=0,
                    total_quantity=0,
                )
                total_price = 0
                total_quantity = 0
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
                    try:
                        response = sc.purchase_product(
                            request=None, store_id=store_id, payload=products_list
                        )
                    except HttpError as e:
                        raise HttpError(400, str(e))

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
                    delivery_information_dict
                )

                if not delivery_result["result"]:
                    raise HttpError(400, "Delivery failed")

                total_price += delivery_result["delivery_fee"]

                payment_details_dict["total_price"] = total_price
                payment_result = payment_service.process_payment(payment_details_dict)
                if not payment_result["result"]:
                    raise HttpError(400, "Payment failed")

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
                "cart_id": purchase.cart.id,
            }

        except CustomUser.DoesNotExist as e:
            raise HttpError(404, "User not found")
        except Cart.DoesNotExist as e:
            raise HttpError(404, "Cart not found")
        except Basket.DoesNotExist as e:
            raise HttpError(404, "Basket not found")
        except BasketProduct.DoesNotExist as e:
            raise HttpError(404, "BasketProduct not found")
        except HttpError as e:
            raise e
        except Exception as e:
            raise HttpError(404, f"{str(e)}")

    # -------------------- Make Bid Purchase --------------------
    def purchase_bid(
        self,
        request,
        user_id: int,
        store_id: int,
        bid_id: int
    ):
        pass    

    # -------------------- Get Delivery Info --------------------
    def get_delivery_info_dict(self, request, user_id: int):
        delivery_information_user = uc.get_delivery_information(request, user_id)
        delivery_information_dict = {
            "address": delivery_information_user["address"],
            "city": delivery_information_user["city"],
            "country": delivery_information_user["country"],
            "zip": delivery_information_user["zip"],
        }
        delivery_information_dict["name"] = uc.get_user_full_name(request, user_id)
        return delivery_information_dict
    
    # -------------------- Get Payment Info --------------------
    def get_payment_info_dict(self, request, user_id: int):
        payment_information_user = uc.get_payment_information(request, user_id)
        payment_details_dict = {
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
        return payment_details_dict