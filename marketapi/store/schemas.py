from datetime import datetime
from typing import Optional

from ninja import Schema


class StoreSchemaIn(Schema):
    name: str
    description: str
    is_active: bool
    created_at: datetime


class StoreSchemaOut(Schema):
    id: int
    name: str
    description: str
    created_at: datetime
    is_active: bool


class RoleSchema(Schema):
    user_id: int
    store: StoreSchemaOut

    class Meta:
        abstract = True


class OwnerSchema(RoleSchema):
    is_founder: bool
    assigned_by: Optional['OwnerSchema'] = None


class ManagerSchema(RoleSchema):
    assigned_by: OwnerSchema


class ManagerPermissionSchemaOut(Schema):
    manager: ManagerSchema
    can_add_product: bool
    can_edit_product: bool
    can_delete_product: bool


class ManagerPermissionSchemaIn(Schema):
    can_add_product: bool
    can_edit_product: bool
    can_delete_product: bool


class PurchasePolicySchemaOut(Schema):
    store: StoreSchemaOut
    max_items_per_purchase: Optional[int]  # Optional
    min_items_per_purchase: Optional[int]  # Optional


class PurchasePolicySchemaIn(Schema):
    max_items_per_purchase: Optional[int]  # Optional
    min_items_per_purchase: Optional[int]  # Optional


class DiscountPolicySchemaOut(Schema):
    store: StoreSchemaOut
    min_items: Optional[int]  # Optional
    min_price: Optional[float]  # Optional


class DiscountPolicySchemaIn(Schema):
    min_items: Optional[int]  # Optional
    min_price: Optional[float]  # Optional


class StoreProductSchemaOut(Schema):
    name: str
    initial_price: float
    quantity: int
    store: StoreSchemaOut


class StoreProductSchemaIn(Schema):
    name: str
    initial_price: float
    quantity: int

#OwnerSchema.update_forward_refs() not sure if needed
