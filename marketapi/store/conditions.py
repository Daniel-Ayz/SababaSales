from typing import List

from .schemas import PurchaseStoreProductSchema

condition_registry = {}


def register_condition(name):
    def decorator(func):
        condition_registry[name] = func
        return func

    return decorator


@register_condition('total_price_greater_than_200')
def condition_total_price_greater_than_200(cart_products: List[PurchaseStoreProductSchema]):
    total = sum([product.price * product.quantity for product in cart_products])
    return total > 200


@register_condition('min_items_5')
def condition_min_items_5(cart_products: List[PurchaseStoreProductSchema]):
    total = sum([product.quantity for product in cart_products])
    return total >= 5
