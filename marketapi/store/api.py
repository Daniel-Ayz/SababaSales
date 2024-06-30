from typing import List, Union
import warnings
from typing import List, Union

from ninja import Router

warnings.filterwarnings("ignore", category=UserWarning)

from .schemas import (
    StoreSchemaIn,
    StoreSchemaOut,
    OwnerSchemaIn,
    ManagerPermissionSchemaIn,
    StoreProductSchemaIn,
    ManagerSchemaIn,
    OwnerSchemaOut,
    RoleSchemaIn,
    StoreProductSchemaOut,
    PurchaseStoreProductSchema,
    RemoveDiscountSchemaIn,
    RemoveOwnerSchemaIn,
    RemoveManagerSchemaIn,
    ManagerSchemaOut,
    SimpleDiscountSchemaIn,
    ConditionalDiscountSchemaIn,
    CompositeDiscountSchemaIn,
    SimpleDiscountSchemaOut,
    ConditionalDiscountSchemaOut,
    CompositeDiscountSchemaOut,
    SearchSchema,
    FilterSearchSchema,
    SimplePurchasePolicySchemaIn,
    ConditionalPurchasePolicySchemaIn,
    CompositePurchasePolicySchemaIn,
    RemovePurchasePolicySchemaIn,
    SimplePurchasePolicySchemaOut,
    ConditionalPurchasePolicySchemaOut,
    CompositePurchasePolicySchemaOut,
    BidSchemaIn,
    BidSchemaOut,
    DecisionBidSchemaIn,
    MakePurchaseOnBidSchemaIn,
    ManagerSchemaInEmail,
    OwnerSchemaInEmail,
    RemoveOwnerSchemaInEmail,
    RemoveManagerSchemaInEmail,
    MakePurchaseOnBidSchemaIn,
    ConditionSchemaOut,
    GetConditionsSchemaIn,
)
from django.shortcuts import get_object_or_404, aget_object_or_404

from .store_controller import StoreController

router = Router()

sc = StoreController()


@router.post("/")
def create_store(request, payload: StoreSchemaIn, user_id: int):
    return sc.create_store(request, payload, user_id)


@router.get("/", response=List[StoreSchemaOut])
def get_stores(request):
    return sc.get_stores(request)


@router.post("/create_fake_data")
def create_fake_data(request):
    return sc.create_fake_data()


@router.get("/search", response=List[StoreProductSchemaOut])
def search_products(
    request, search_query: SearchSchema, filter_query: FilterSearchSchema
):
    return sc.search_products(request, search_query, filter_query)


@router.get("/manager_or_owner", response=List[StoreSchemaOut])
def get_stores_that_manager_or_owner(request, user_id: int):
    return sc.get_stores_that_manager_or_owner(request, user_id)


@router.get("/{store_id}", response=StoreSchemaOut)
def get_store(request, store_id: int):
    return sc.get_store(request, store_id)


@router.post("/{store_id}/assign_owner")
def assign_owner(request, payload: OwnerSchemaIn):
    return sc.assign_owner(request, payload)


@router.delete("/{store_id}/remove_owner")
def remove_owner(request, payload: RemoveOwnerSchemaIn):
    return sc.remove_owner(request, payload)


@router.post("/{store_id}/assign_owner_email")
def assign_owner(request, payload: OwnerSchemaInEmail):
    return sc.assign_owner(request, payload)


@router.delete("/{store_id}/remove_owner_email")
def remove_owner(request, payload: RemoveOwnerSchemaInEmail):
    return sc.remove_owner(request, payload)


@router.delete("/{store_id}/leave_ownership")
def leave_ownership(request, payload: RoleSchemaIn):
    return sc.leave_ownership(request, payload)


@router.post("/{store_id}/assign_manager")
def assign_manager(request, payload: ManagerSchemaIn):
    return sc.assign_manager(request, payload)


@router.delete("/{store_id}/remove_manager")
def remove_manager(request, payload: RemoveManagerSchemaIn):
    return sc.remove_manager(request, payload)


@router.post("/{store_id}/assign_manager_email")
def assign_manager(request, payload: ManagerSchemaInEmail):
    return sc.assign_manager(request, payload)


@router.delete("/{store_id}/remove_manager_email")
def remove_manager(request, payload: RemoveManagerSchemaInEmail):
    return sc.remove_manager(request, payload)


@router.post("/{store_id}/change_manager_permissions")
def assign_manager_permissions(
    request,
    payload: ManagerPermissionSchemaIn,
    manager: RoleSchemaIn,
    assigning_owner_id: int,
):
    return sc.assign_manager_permissions(request, payload, manager, assigning_owner_id)


@router.get("/{store_id}/get_manager_permissions")
def get_manager_permissions(request, role: RoleSchemaIn, manager_id: int):
    return sc.get_manager_permissions(request, role, manager_id)


@router.put("stores/{store_id}/close_store")
def close_store(request, payload: RoleSchemaIn):
    return sc.close_store(request, payload)


@router.put("stores/{store_id}/reopen_store")
def reopen_store(request, payload: RoleSchemaIn):
    return sc.reopen_store(request, payload)


@router.get("/{store_id}/get_owners", response=List[OwnerSchemaOut])
def get_owners(request, payload: RoleSchemaIn):
    return sc.get_owners(request, payload)


@router.get("/{store_id}/get_managers", response=List[ManagerSchemaOut])
def get_managers(request, payload: RoleSchemaIn):
    return sc.get_managers(request, payload)


@router.post("/{store_id}/add_purchase_policy")
def add_purchase_policy(
    request,
    role: RoleSchemaIn,
    payload: Union[
        SimplePurchasePolicySchemaIn,
        ConditionalPurchasePolicySchemaIn,
        CompositePurchasePolicySchemaIn,
    ],
):
    return sc.add_purchase_policy(request, role, payload).get("message")


@router.delete("/{store_id}/remove_purchase_policy")
def remove_purchase_policy(
    request, role: RoleSchemaIn, payload: RemovePurchasePolicySchemaIn
):
    return sc.remove_purchase_policy(request, role, payload)


@router.post(
    "/{store_id}/get_purchase_policies",
    response=List[
        Union[
            SimplePurchasePolicySchemaOut,
            ConditionalPurchasePolicySchemaOut,
            CompositePurchasePolicySchemaOut,
        ]
    ],
)
def get_purchase_policies(request, role: RoleSchemaIn):
    return sc.get_purchase_policies(request, role)


@router.post("/{store_id}/add_discount_policy")
def add_discount_policy(
    request,
    role: RoleSchemaIn,
    payload: Union[
        SimpleDiscountSchemaIn, ConditionalDiscountSchemaIn, CompositeDiscountSchemaIn
    ],
):  # SimpleDiscountSchemaIn | ConditionalDiscountSchemaIn | CompositeDiscountSchemaIn
    return sc.add_discount_policy(request, role, payload).get("message")


@router.delete("/{store_id}/remove_discount_policy")
def remove_discount_policy(
    request, role: RoleSchemaIn, payload: RemoveDiscountSchemaIn
):
    return sc.remove_discount_policy(request, role, payload)


@router.post(
    "/{store_id}/get_discount_policies",
    response=List[
        Union[
            SimpleDiscountSchemaOut,
            ConditionalDiscountSchemaOut,
            CompositeDiscountSchemaOut,
        ]
    ],
)
def get_discount_policies(request, role: RoleSchemaIn):
    return sc.get_discount_policies(request, role)


@router.post("/{store_id}/get_conditions", response=List[ConditionSchemaOut])
def get_conditions(request, payload: GetConditionsSchemaIn):
    return sc.get_conditions(request, payload)


@router.post("/{store_id}/add_product")
def add_product(request, role: RoleSchemaIn, payload: StoreProductSchemaIn):
    return sc.add_product(request, role, payload)


@router.delete("/{store_id}/remove_product")
def remove_product(request, role: RoleSchemaIn, product_name: str):
    return sc.remove_product(request, role, product_name)


@router.put("/{store_id}/edit_product")
def edit_product(request, role: RoleSchemaIn, payload: StoreProductSchemaIn):
    return sc.edit_product(request, role, payload)


@router.get("/{store_id}/get_products", response=List[StoreProductSchemaOut])
def get_products(request, store_id: int, role: RoleSchemaIn):
    return sc.get_products(request, store_id, role)


@router.get("/{store_id}/products", response=List[StoreProductSchemaOut])
def get_products(request, store_id: int):
    return sc.get_product_clean(request, store_id)


@router.put("/{store_id}/purchase_product")
def purchase_product(request, store_id: int, payload: List[PurchaseStoreProductSchema]):
    real_payload = []
    # for tup in payload:
    #     real_payload.append(PurchaseStoreProductSchema(tup[0], tup[1]))
    return sc.purchase_product(request, store_id, payload)


@router.post("/{store_id}/make_bid")
def make_bid(request, payload: BidSchemaIn):
    return sc.make_bid(request, payload)


@router.put("/{store_id}/decide_on_bid")
def decide_on_bid(request, role: RoleSchemaIn, payload: DecisionBidSchemaIn):
    return sc.decide_on_bid(request, role, payload)


@router.get("/{store_id}/get_bids", response=List[BidSchemaOut])
def get_bids(request, role: RoleSchemaIn, store_id: int):
    return sc.get_bids(request, role, store_id)


@router.put("/{store_id}/make_purchase_on_bid")
def make_purchase_on_bid(request, payload: MakePurchaseOnBidSchemaIn):
    return sc.make_purchase_on_bid(request, payload)


# @router.put("/{store_id}/return_products")
# def return_products(request, store_id: int, payload: List[PurchaseStoreProductSchema]):
#     return sc.return_products(request, store_id, payload)
