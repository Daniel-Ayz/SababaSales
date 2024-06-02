from datetime import datetime
from typing import Optional, Union

from ninja import Schema


class StoreSchemaIn(Schema):
    name: str
    description: str
    #created_at: datetime added automatically


class StoreSchemaOut(Schema):
    id: int
    name: str
    description: str
    created_at: datetime
    is_active: bool


class RoleSchemaIn(Schema):
    user_id: int
    store_id: int

    class Meta:
        abstract = True


class OwnerSchemaIn(RoleSchemaIn):
    assigned_by: int


class RemoveOwnerSchemaIn(RoleSchemaIn):
    removed_by: int


class ManagerSchemaIn(RoleSchemaIn):
    assigned_by: int


class RemoveManagerSchemaIn(RoleSchemaIn):
    removed_by: int


class RoleSchemaOut(Schema):
    user_id: int
    store: StoreSchemaOut

    class Meta:
        abstract = True


class OwnerSchemaOut(RoleSchemaOut):
    is_founder: bool
    assigned_by: Optional['OwnerSchemaOut'] = None


class ManagerSchemaOut(RoleSchemaOut):
    assigned_by: OwnerSchemaOut


class ManagerPermissionSchemaOut(Schema):
    manager: ManagerSchemaOut
    can_add_product: Optional[bool]
    can_edit_product: Optional[bool]
    can_delete_product: Optional[bool]
    can_add_purchase_policy: Optional[bool]
    can_add_discount_policy: Optional[bool]
    can_remove_purchase_policy: Optional[bool]
    can_remove_discount_policy: Optional[bool]


class ManagerPermissionSchemaIn(Schema):
    can_add_product: Optional[bool] = False
    can_edit_product: Optional[bool] = False
    can_delete_product: Optional[bool] = False
    can_add_purchase_policy: Optional[bool] = False
    can_add_discount_policy: Optional[bool] = False
    can_remove_purchase_policy: Optional[bool] = False
    can_remove_discount_policy: Optional[bool] = False


class PurchasePolicySchemaOut(Schema):
    store: StoreSchemaOut
    max_items_per_purchase: Optional[int] = None  # Optional
    min_items_per_purchase: Optional[int] = None  # Optional


class PurchasePolicySchemaIn(Schema):
    max_items_per_purchase: Optional[int] = None  # Optional
    min_items_per_purchase: Optional[int] = None  # Optional


class StoreProductSchemaOut(Schema):
    name: str
    initial_price: float
    quantity: int
    store: StoreSchemaOut
    category: str


class StoreProductSchemaIn(Schema):
    name: str
    initial_price: float
    quantity: int
    category: str


class PurchaseStoreProductSchema(Schema):
    product_name: str
    quantity: int
    category: str


class RemoveDiscountSchemaIn(Schema):
    store_id: int
    discount_id: int


class DiscountBaseSchemaIn(Schema):
    store_id: int
    #id: Optional[int] = None
    #discount_type: str
    is_root: bool

    class Meta:
        abstract = True


class SimpleDiscountSchemaIn(DiscountBaseSchemaIn):
    percentage: float
    applicable_products: Optional[list[str]] = None
    applicable_categories: Optional[list[str]] = None


class ConditionalDiscountSchemaIn(DiscountBaseSchemaIn):
    condition_name: str
    discount: Union[SimpleDiscountSchemaIn, 'ConditionalDiscountSchemaIn', 'CompositeDiscountSchemaIn']


class CompositeDiscountSchemaIn(DiscountBaseSchemaIn):
    discounts: list[Union[SimpleDiscountSchemaIn, ConditionalDiscountSchemaIn, 'CompositeDiscountSchemaIn']]
    combine_function: str
    conditions: list[str]


class DiscountBaseSchemaOut(Schema):
    store: StoreSchemaOut
    id: int
    #discount_type: str
    is_root: bool

    class Meta:
        abstract = True


class SimpleDiscountSchemaOut(DiscountBaseSchemaOut):
    percentage: float
    applicable_products: Optional[list[StoreProductSchemaOut]] = None
    applicable_categories: Optional[str] = '[]'


class ConditionalDiscountSchemaOut(DiscountBaseSchemaOut):
    condition_name: str
    discount: Union[SimpleDiscountSchemaOut, 'ConditionalDiscountSchemaOut', 'CompositeDiscountSchemaOut']


class CompositeDiscountSchemaOut(DiscountBaseSchemaOut):
    discounts: list[Union[SimpleDiscountSchemaOut, ConditionalDiscountSchemaOut, 'CompositeDiscountSchemaOut']]
    combine_function: str
    conditions: str


class SearchSchema(Schema):
    product_name: Optional[str] = None
    category: Optional[str] = None
    store_id: Optional[int] = None


class FilterSearchSchema(Schema):
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_quantity: Optional[int] = None
    max_quantity: Optional[int] = None

# class DiscountPolicySchemaOut(Schema):
#     store: StoreSchemaOut
#     min_items: Optional[int] = None  # Optional
#     min_price: Optional[float] = None  # Optional
#
#
# class DiscountPolicySchemaIn(Schema):
#     min_items: Optional[int] = None  # Optional
#     min_price: Optional[float] = None  # Optional


#OwnerSchema.update_forward_refs() not sure if needed
