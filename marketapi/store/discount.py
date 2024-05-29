from abc import ABC, abstractmethod
from typing import List

from .schemas import PurchaseStoreProductSchema
from .conditions import condition_registry


class Discount(ABC):
    @abstractmethod
    def apply_discount(self, price: float) -> float:
        pass


class SimpleDiscount(Discount):
    def __init__(self, percentage: float, applicable_products: List[str]):
        self.percentage = percentage
        self.applicable_products = applicable_products

    def apply_discount(self, cart_products: List[PurchaseStoreProductSchema]) -> float:
        discount = 0
        for product in cart_products:
            if product.product_name in self.applicable_products:
                discount += product.quantity * product.price * self.percentage / 100
        return discount


class ConditionalDiscount(Discount):
    def __init__(self, condition_name, discount):
        self.condition_name = condition_name
        self.discount = discount

    def apply_discount(self, cart_products: List[PurchaseStoreProductSchema]):
        condition_func = condition_registry.get(self.condition_name)
        if condition_func(cart_products):
            return self.discount.apply_discount(cart_products)
        return 0


class CompositeDiscount(Discount):
    def __init__(self, discounts, combine_function):
        self.discounts = discounts
        self.combine_function = combine_function

    def apply_discount(self, cart_products: List[PurchaseStoreProductSchema]):
        discount = [discount.apply_discount(cart_products) for discount in self.discounts]
        combine_operations = {
            'sum': sum_discounts,
            'max': max_discount,
            'logical_and': logical_and,
            'logical_or': logical_or,
            'logical_xor': logical_xor
        }
        return combine_operations[self.combine_function](discount)





def logical_and(discounts):
    return all(discount > 0 for discount in discounts)


def logical_or(discounts):
    return any(discount > 0 for discount in discounts)


def logical_xor(discounts):
    return sum(1 for discount in discounts if discount > 0) == 1


def sum_discounts(discounts):
    return sum(discounts)


def max_discount(discounts):
    return max(discounts)
