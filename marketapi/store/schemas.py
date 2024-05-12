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

class ManagerPermissionSchema(Schema):
    manager: ManagerSchema
    can_add_product: bool
    can_edit_product: bool
    can_delete_product: bool

class PurchasePolicySchema(Schema):
    store: StoreSchemaOut
    max_items_per_purchase: Optional[int]  # Optional
    min_items_per_purchase: Optional[int]  # Optional

class DiscountPolicySchema(Schema):
    store: StoreSchemaOut
    min_items: Optional[int]  # Optional
    min_price: Optional[float]  # Optional
    discount: float


#OwnerSchema.update_forward_refs() not sure if needed

