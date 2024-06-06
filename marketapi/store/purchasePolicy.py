import operator
from abc import ABC, abstractmethod
from functools import reduce
from typing import List

from .conditions import build_condition_funcs, combine_operations
from .models import StoreProduct, Store, Condition
from .schemas import PurchaseStoreProductSchema


#from .conditions import condition_registry

class PurchasePolicy(ABC):
    @abstractmethod
    def apply_policy(self, cart_products: List[PurchaseStoreProductSchema]) -> bool:
        pass


class SimplePurchasePolicyClass(PurchasePolicy):
    def __init__(self, store: Store, condition: Condition):
        self.store = store
        self.condition = condition

    def apply_policy(self, cart_products: List[PurchaseStoreProductSchema]) -> bool:
        condition_func = build_condition_funcs(self.condition)[0]
        products = [StoreProduct.objects.get(name=product.product_name, store=self.store) for product in cart_products]
        return condition_func(cart_products, products)


class ConditionalPurchasePolicyClass(PurchasePolicy):
    def __init__(self, condition: PurchasePolicy, store, restriction: PurchasePolicy):
        self.condition = condition
        self.store = store
        self.restriction = restriction

    def apply_policy(self, cart_products: List[PurchaseStoreProductSchema]) -> bool:
        if not self.condition.apply_policy(cart_products):  #the condition doesnt apply - for example has eggplants
            return not self.restriction.apply_policy(cart_products)  #if no eggplants - cant purchase over 5 tomatos
        #contrapositive of the condition
        return True  #if the condition applies, the restriction doesnt apply


class CompositePurchasePolicyClass(PurchasePolicy):
    def __init__(self, policies: List[PurchasePolicy], combine_function, store):
        self.policies = policies
        self.combine_function = combine_function
        self.store = store

    def apply_policy(self, cart_products: List[PurchaseStoreProductSchema]) -> bool:
        if self.combine_function == "logical_and":
            return reduce(operator.and_, [condition.apply_policy(cart_products) for condition in self.policies])
        elif self.combine_function == "logical_or":
            return reduce(operator.or_, [condition.apply_policy(cart_products) for condition in self.policies])
