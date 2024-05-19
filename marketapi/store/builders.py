from abc import ABC, abstractmethod

from schemas import ManagerPermissionSchemaIn, PurchasePolicySchemaIn, DiscountPolicySchemaIn


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
    def with_can_add_purchase_policy(self):
        pass

    @abstractmethod
    def with_can_add_discount_policy(self):
        pass

    @abstractmethod
    def with_can_remove_purchase_policy(self):
        pass

    @abstractmethod
    def with_can_remove_discount_policy(self):
        pass

    @abstractmethod
    def build(self) -> ManagerPermissionSchemaIn:
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

    def with_can_add_purchase_policy(self):
        self.permissions["can_add_purchase_policy"] = True

    def with_can_add_discount_policy(self):
        self.permissions["can_add_discount_policy"] = True

    def with_can_remove_purchase_policy(self):
        self.permissions["can_remove_purchase_policy"] = True

    def with_can_remove_discount_policy(self):
        self.permissions["can_remove_discount_policy"] = True

    def build(self) -> ManagerPermissionSchemaIn:
        return ManagerPermissionSchemaIn(
            **self.permissions,
        )


def create_full_manager_permissions():
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
    def with_max_items_per_purchase(self, max_items_per_purchase):
        pass

    @abstractmethod
    def with_min_items_per_purchase(self, min_items_per_purchase):
        pass

    @abstractmethod
    def build(self) -> PurchasePolicySchemaIn:
        pass


class ConcretePurchasePolicyBuilder(PurchasePolicyBuilder):
    def __init__(self):
        self.policy = {}  # Dictionary to store set policies

    def with_max_items_per_purchase(self, max_items_per_purchase):
        self.policy["max_items_per_purchase"] = max_items_per_purchase

    def with_min_items_per_purchase(self, min_items_per_purchase):
        self.policy["min_items_per_purchase"] = min_items_per_purchase

    def build(self) -> PurchasePolicySchemaIn:
        return PurchasePolicySchemaIn(
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
    def with_min_items(self, min_items):
        pass

    @abstractmethod
    def with_min_price(self, min_price):
        pass

    @abstractmethod
    def build(self) -> DiscountPolicySchemaIn:
        pass


class ConcreteDiscountPolicyBuilder(DiscountPolicyBuilder):
    def __init__(self):
        self.policy = {}  # Dictionary to store set policies

    def with_min_items(self, min_items):
        self.policy["min_items"] = min_items

    def with_min_price(self, min_price):
        self.policy["min_price"] = min_price

    def build(self) -> DiscountPolicySchemaIn:
        return DiscountPolicySchemaIn(
            **self.policy,
        )


def create_discount_policy(min_items, min_price):
    builder = ConcreteDiscountPolicyBuilder()
    builder.with_min_items(min_items)
    builder.with_min_price(min_price)

    return builder.build()

#----------------------------------------------DiscountPolicyBuilder----------------------------------------------
