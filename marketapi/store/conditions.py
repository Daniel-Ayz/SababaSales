from datetime import datetime
from typing import List

from .models import Condition, StoreProduct
from .schemas import PurchaseStoreProductSchema

import operator

operator_map = {
    "at_least": operator.ge,
    "at_most": operator.le,
    "equal_to": operator.eq,
    "not_equal_to": operator.ne,
    "greater_than": operator.gt,
    "less_than": operator.lt,
}




def evaluate_condition(operator_name, value1, value2):
    if operator_name in operator_map:
        return operator_map[operator_name](value1, value2)
    else:
        raise ValueError(f"Operator {operator_name} is not supported.")


def build_product_condition(conditionModel: Condition):
    def product_condition(cart_products: List[PurchaseStoreProductSchema], products: List[StoreProduct]):
        total = sum(
            [product.quantity for product in cart_products if product.product_name == conditionModel.name_of_apply])
        return evaluate_condition(conditionModel.condition, total, conditionModel.value)

    return product_condition


def build_category_condition(conditionModel):
    def category_condition(cart_products: List[PurchaseStoreProductSchema], products: List[StoreProduct]):
        total = sum([product.quantity for product in cart_products
                     if (product.category == conditionModel.name_of_apply or conditionModel.name_of_apply == "all")])
        return evaluate_condition(conditionModel.condition, total, conditionModel.value)

    return category_condition


def build_price_condition(conditionModel):
    def price_condition(cart_products: List[PurchaseStoreProductSchema], products: List[StoreProduct]):
        total = sum(
            [store_product.initial_price * product.quantity for store_product, product in zip(products, cart_products)])
        return evaluate_condition(conditionModel.condition, total, conditionModel.value)

    return price_condition


def build_time_condition(conditionModel):
    def time_condition(cart_products: List[PurchaseStoreProductSchema], products: List[StoreProduct]):
        current_hour = datetime.now().hour
        # total = sum([product.quantity for product in cart_products
        #              if (product.category == conditionModel.name_of_apply or conditionModel.name_of_apply == "all"
        #                  or product.product_name == conditionModel.name_of_apply)]) #check products or categories this applies to
        return evaluate_condition(conditionModel.condition, current_hour, conditionModel.value)

    return time_condition


def build_condition_funcs(conditions):
    funcs = []
    for conditionModel in conditions:
        condition_name = conditionModel.applies_to
        if condition_name == "product":
            funcs.append(build_product_condition(conditionModel))
        elif condition_name == "category":
            funcs.append(build_category_condition(conditionModel))
        elif condition_name == "price":
            funcs.append(build_price_condition(conditionModel))
        elif condition_name == "time":
            funcs.append(build_time_condition(conditionModel))
    return funcs


def logical_and(condition_funcs, cart_products, products):
    return all(func(cart_products, products) for func in condition_funcs)


def logical_or(condition_funcs, cart_products, products):
    return any(func(cart_products, products) for func in condition_funcs)


def logical_xor(condition_funcs, cart_products, products):
    return sum(func(cart_products, products) for func in condition_funcs) == 1


combine_operations = {
            'logical_and': logical_and,
            'logical_or': logical_or,
            'logical_xor': logical_xor,
        }
