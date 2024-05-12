from abc import ABC, abstractmethod

from schemas import ManagerPermissionSchema, ManagerSchema, PurchasePolicySchema, DiscountPolicySchema


#----------------------------------------------ManagerPermissionBuilder----------------------------------------------
class ManagerPermissionBuilder(ABC):
    @abstractmethod
    def with_can_add_product(self):
        pass

    @abstractmethod
    def with_can_edit_product(self):
        pass

    @abstractmethod
    def with_can_delete_product(self):
        pass

    @abstractmethod
    def build(self) -> ManagerPermissionSchema:
        """Builds and returns the ManagerPermissionSchema object."""
        pass


class ConcreteManagerPermissionBuilder(ManagerPermissionBuilder):
    def __init__(self):
        self.permissions = {}  # Dictionary to store set permissions

    def with_can_add_product(self):
        self.permissions["can_add_product"] = True

    def with_can_edit_product(self):
        self.permissions["can_edit_product"] = True

    def with_can_delete_product(self):
        self.permissions["can_delete_product"] = True

    def build(self) -> ManagerPermissionSchema:
        return ManagerPermissionSchema(
            **self.permissions,
        )


def create_full_manager_permissions(manager_schema):
    builder = ManagerPermissionBuilder()
    builder.with_can_add_product()
    builder.with_can_edit_product()

    return builder.build()


# manager_schema = ManagerSchema()
# full_manager_permissions = create_full_manager_permissions(manager_schema)


#----------------------------------------------ManagerPermissionBuilder----------------------------------------------


#----------------------------------------------PurchasePolicyBuilder----------------------------------------------
class PurchasePolicyBuilder(ABC):
    @abstractmethod
    def with_max_items_per_purchase(self):
        pass

    @abstractmethod
    def with_min_items_per_purchase(self):
        pass

    @abstractmethod
    def build(self):
        pass


class ConcretePurchasePolicyBuilder(PurchasePolicyBuilder):
    def __init__(self):
        self.policy = {}  # Dictionary to store set policies

    def with_max_items_per_purchase(self, max_items_per_purchase):
        self.policy["max_items_per_purchase"] = max_items_per_purchase

    def with_min_items_per_purchase(self, min_items_per_purchase):
        self.policy["min_items_per_purchase"] = min_items_per_purchase

    def build(self):
        return PurchasePolicySchema(
            **self.policy,
        )


def create_purchase_policy(max_items_per_purchase, min_items_per_purchase):
    builder = ConcretePurchasePolicyBuilder()
    builder.with_max_items_per_purchase(max_items_per_purchase)
    builder.with_min_items_per_purchase(min_items_per_purchase)

    return builder.build()


#----------------------------------------------PurchasePolicyBuilder----------------------------------------------

#----------------------------------------------DiscountPolicyBuilder----------------------------------------------
class DiscountPolicyBuilder(ABC):
    @abstractmethod
    def with_min_items(self):
        pass

    @abstractmethod
    def with_min_price(self):
        pass

    @abstractmethod
    def with_discount(self):
        pass

    @abstractmethod
    def build(self):
        pass


class ConcreteDiscountPolicyBuilder(DiscountPolicyBuilder):
    def __init__(self):
        self.policy = {}  # Dictionary to store set policies

    def with_min_items(self, min_items):
        self.policy["min_items"] = min_items

    def with_min_price(self, min_price):
        self.policy["min_price"] = min_price

    def with_discount(self, discount):
        self.policy["discount"] = discount

    def build(self):
        return DiscountPolicySchema(
            **self.policy,
        )


def create_discount_policy(min_items, min_price):
    builder = ConcreteDiscountPolicyBuilder()
    builder.with_min_items(min_items)
    builder.with_min_price(min_price)

    return builder.build()

#----------------------------------------------DiscountPolicyBuilder----------------------------------------------
