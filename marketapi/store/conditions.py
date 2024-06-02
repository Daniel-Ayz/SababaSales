from typing import List

from .models import Store, StoreProduct
from .schemas import PurchaseStoreProductSchema

condition_registry = {}


def register_condition(name):
    def decorator(func):
        condition_registry[name] = func
        return func

    return decorator


@register_condition('total_price_greater_than_200')
def condition_total_price_greater_than_200(cart_products: List[PurchaseStoreProductSchema], products: List[StoreProduct]):
    total = sum([store_product.initial_price * product.quantity for store_product, product in zip(products, cart_products)])
    return total > 200


@register_condition('has_dairy')
def condition_has_dairy(cart_products: List[PurchaseStoreProductSchema], products: List[StoreProduct]):
    return any([product.category in ['Dairy'] for product in cart_products])


@register_condition('has_pastries')
def condition_has_pastry(cart_products: List[PurchaseStoreProductSchema], products: List[StoreProduct]):
    return any([product.category in ['Pastry'] for product in cart_products])


@register_condition('min_items_5')
def condition_min_items_5(cart_products: List[PurchaseStoreProductSchema], products: List[StoreProduct]):
    total = sum([product.quantity for product in cart_products])
    return total >= 5


@register_condition('at_least_5_buns')
def condition_at_least_5_buns(cart_products: List[PurchaseStoreProductSchema], products: List[StoreProduct]):
    total = sum([product.quantity for product in cart_products if product.product_name == 'Bun'])
    return total >= 5


@register_condition('at_least_2_bread_loafs')
def condition_at_most_2_bread_loafs(cart_products: List[PurchaseStoreProductSchema], products: List[StoreProduct]):
    total = sum([product.quantity for product in cart_products if product.product_name == 'Bread Loaf'])
    return total >= 2


@register_condition('at_least_3_cottage_cheese')
def condition_at_least_3_cottage_cheese(cart_products: List[PurchaseStoreProductSchema], products: List[StoreProduct]):
    total = sum([product.quantity for product in cart_products if product.product_name == 'Cottage Cheese'])
    return total >= 3


@register_condition('at_least_2_yogurts')
def condition_at_most_2_yogurts(cart_products: List[PurchaseStoreProductSchema], products: List[StoreProduct]):
    total = sum([product.quantity for product in cart_products if product.product_name == 'Yogurt'])
    return total >= 2


@register_condition('total_price_greater_than_100')
def condition_total_price_greater_than_100(cart_products: List[PurchaseStoreProductSchema], products: List[StoreProduct]):
    total = sum(
        [store_product.initial_price * product.quantity for store_product, product in zip(products, cart_products)])
    return total > 100


@register_condition('at_least_3_pastas')
def condition_at_least_3_pastas(cart_products: List[PurchaseStoreProductSchema], products: List[StoreProduct]):
    total = sum([product.quantity for product in cart_products if product.product_name == 'Pasta'])
    return total >= 3
