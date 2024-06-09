from abc import ABC, abstractmethod
from typing import List

from .conditions import build_condition_funcs, combine_operations
from .models import StoreProduct, Store, Condition
from .schemas import PurchaseStoreProductSchema


#from .conditions import condition_registry

class Discount(ABC):
    @abstractmethod
    def apply_discount(self, price: float) -> float:
        pass


class SimpleDiscountClass(Discount):
    def __init__(self, percentage: float, applicable_products: List[StoreProduct], store: Store,
                 applicable_categories: List[str] = None):
        self.percentage = percentage
        self.applicable_products = applicable_products
        self.applicable_categories = applicable_categories
        self.store = store
        self.product_names = [product.name for product in self.applicable_products]

    def apply_discount(self, cart_products: List[PurchaseStoreProductSchema]) -> float:
        discount = 0

        for product in cart_products:
            if product.product_name in self.product_names:
                target_product = next(
                    (prod for prod in self.applicable_products if prod.name == product.product_name), None)
                price = target_product.initial_price * product.quantity
                discount += price * self.percentage / 100
            elif self.applicable_categories is not None and (
                    product.category in self.applicable_categories or self.applicable_categories == ["all"]):
                item = StoreProduct.objects.get(name=product.product_name, store=self.store)
                price = item.initial_price * product.quantity
                discount += price * self.percentage / 100
        return discount


class ConditionalDiscountClass(Discount):
    def __init__(self, condition_name, discount, store):
        self.condition_name = condition_name
        self.discount = discount
        self.store = store

    def apply_discount(self, cart_products: List[PurchaseStoreProductSchema]):
        condition_func = build_condition_funcs(self.condition_name)[0]
        products = [StoreProduct.objects.get(name=product.product_name, store=self.store) for product in cart_products]
        if condition_func(cart_products, products):
            return self.discount.apply_discount(cart_products)
        return 0


class CompositeDiscountClass(Discount):
    def __init__(self, discounts, combine_function, conditions: List[Condition], store):
        self.discounts = discounts
        self.combine_function = combine_function
        self.conditions = conditions
        self.store = store

    def apply_discount(self, cart_products: List[PurchaseStoreProductSchema]):

        products = [StoreProduct.objects.get(name=product.product_name, store=self.store) for product in cart_products]
        condition_funcs = build_condition_funcs(self.conditions)
        if self.combine_function == 'max':
            return max(discount.apply_discount(cart_products) for discount in self.discounts)
        if combine_operations[self.combine_function](condition_funcs, cart_products, products):
            return sum(discount.apply_discount(cart_products) for discount in self.discounts)
