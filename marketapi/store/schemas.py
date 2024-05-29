from datetime import datetime
from typing import Optional

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


class DiscountBaseSchema(Schema):
    store_id: int
    discount_type: str

    class Meta:
        abstract = True


class SimpleDiscountSchema(DiscountBaseSchema):
    percentage: float
    applicable_products: list[str]


class ConditionalDiscountSchema(DiscountBaseSchema):
    condition_name: str
    discount: DiscountBaseSchema


class CompositeDiscountSchema(DiscountBaseSchema):
    discounts: list[DiscountBaseSchema]
    combine_function: str


# class DiscountPolicySchemaOut(Schema):
#     store: StoreSchemaOut
#     min_items: Optional[int] = None  # Optional
#     min_price: Optional[float] = None  # Optional
#
#
# class DiscountPolicySchemaIn(Schema):
#     min_items: Optional[int] = None  # Optional
#     min_price: Optional[float] = None  # Optional


class StoreProductSchemaOut(Schema):
    name: str
    initial_price: float
    quantity: int
    store: StoreSchemaOut


class StoreProductSchemaIn(Schema):
    name: str
    initial_price: float
    quantity: int


class PurchaseStoreProductSchema(Schema):
    product_name: str
    quantity: int

#OwnerSchema.update_forward_refs() not sure if needed
