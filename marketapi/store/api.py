from typing import List

from django.http import HttpResponse
from ninja import Router

from .models import Store, Owner, Manager, ManagerPermission, PurchasePolicy, DiscountPolicy, StoreProduct
from .schemas import StoreSchemaIn, StoreSchemaOut, OwnerSchemaIn, ManagerPermissionSchemaIn, PurchasePolicySchemaIn, \
    DiscountPolicySchemaIn, StoreProductSchemaIn, ManagerSchemaIn, OwnerSchemaOut, RoleSchemaIn, StoreProductSchemaOut, \
    PurchaseStoreProductSchema
from django.shortcuts import get_object_or_404, aget_object_or_404

router = Router()

@router.get("/check")
def check(request):
    return {"message": "Store API is working"}

@router.get("/stores/{store_id}", response=StoreSchemaOut)
async def get_store(request, store_id: int):
    return await aget_object_or_404(Store, pk=store_id)


@router.post("/stores")
async def create_store(request, payload: StoreSchemaIn, role: RoleSchemaIn):
    store = await Store.objects.acreate(**payload.dict())
    await Owner.objects.acreate(
        user_id=role.user_id,
        store=store,
        is_founder=True
    )
    return {"id": store.id}


@router.post("/stores/{store_id}/assign_owner")
async def assign_owner(request, payload: OwnerSchemaIn):
    store = await aget_object_or_404(Store, pk=payload.store_id)
    assigning_owner = await aget_object_or_404(Owner, user_id=payload.assigned_by, store=store)
    if Owner.objects.afilter(user_id=payload.user_id, store=store).exists():
        raise ValueError("User is already an owner")

    owner = Owner.objects.create(
        user_id=payload.user_id,
        assigned_by=assigning_owner,
        store=store,
        is_founder=payload.is_founder
    )
    return {"message": "Owner assigned successfully"}


@router.delete("/stores/{store_id}/remove_owner")
def remove_owner(request, payload: OwnerSchemaIn):
    store = get_object_or_404(Store, pk=payload.store_id)
    removing_owner = get_object_or_404(Owner, user_id=payload.removed_by, store=store)
    removed_owner = get_object_or_404(Owner, user_id=payload.user_id, store=store)

    if removed_owner.assigned_by != removing_owner:
        raise ValueError("Owner can only be removed by the owner who assigned them")

    removed_owner.delete()
    return {"message": "Owner removed successfully"}


@router.delete("/stores/{store_id}/leave_ownership")
def leave_ownership(request, payload: OwnerSchemaIn):
    store = get_object_or_404(Store, pk=payload.store_id)
    owner = get_object_or_404(Owner, user_id=payload.user_id, store=store)
    if owner.is_founder:
        raise ValueError("Founder cannot leave ownership")

    owner.delete()
    return {"message": "Ownership left successfully"}


@router.post("/stores/{store_id}/assign_manager")
def assign_manager(request, payload: ManagerSchemaIn):
    store = get_object_or_404(Store, pk=payload.store_id)
    assigning_owner = get_object_or_404(Owner, user_id=payload.assigned_by, store=store)
    if Manager.objects.filter(user_id=payload.user_id, store=store).exists():
        raise ValueError("User is already a manager")
    elif Owner.objects.filter(user_id=payload.user_id, store=store).exists():
        raise ValueError("User is already an owner")

    if not Owner.objects.filter(user_id=payload.assigned_by, store=store).exists():
        raise ValueError("Only owners can assign managers")

    manager = Manager.objects.create(
        user_id=payload.user_id,
        assigned_by=assigning_owner,
        store=store
    )
    return {"message": "Manager assigned successfully"}


@router.delete("/stores/{store_id}/remove_manager")
def remove_manager(request, payload: OwnerSchemaIn):
    store = get_object_or_404(Store, pk=payload.store_id)
    removing_owner = get_object_or_404(Owner, user_id=payload.removed_by, store=store)
    removed_manager = get_object_or_404(Manager, user_id=payload.user_id, store=store)

    if removed_manager.assigned_by != removing_owner:
        raise ValueError("Manager can only be removed by the owner who assigned them")

    removed_manager.delete()
    return {"message": "Manager removed successfully"}


@router.post("/stores/{store_id}/change_manager_permissions")
def assign_manager_permissions(request, payload: ManagerPermissionSchemaIn, manager: RoleSchemaIn,
                               assigning_owner_id: int):
    store = get_object_or_404(Store, pk=manager.store_id)
    manager = get_object_or_404(Manager, user_id=manager.user_id, store=store)
    assigning_owner = get_object_or_404(Owner, user_id=assigning_owner_id, store=store)
    if not Owner.objects.filter(user_id=assigning_owner_id, store=store).exists():
        raise ValueError("Only owners can assign permissions")
    try:
        existing_permission, _ = ManagerPermission.objects.update_or_create(
            manager=manager,
            defaults=payload.dict()
        )
    except Exception as e:
        return HttpResponse(status=500, content=f"Error assigning permissions: {str(e)}")

    return {"message": "Manager permissions assigned successfully"}


# @router.get("/stores/{store_id}/get_manager_permissions")
# def get_manager_permissions(request, store_id: int, manager_id: int):
#     store = get_object_or_404(Store, pk=store_id)
#     manager = get_object_or_404(Manager, pk=manager_id, store=store)
#
#     permissions = get_object_or_404(ManagerPermission, manager=manager)
#
#     return permissions

@router.put("stores/{store_id}/close_store")
def close_store(request, payload: RoleSchemaIn):
    store = get_object_or_404(Store, pk=payload.store_id)
    owner = get_object_or_404(Owner, user_id=payload.user_id, store=store)
    if not owner.is_founder:
        raise ValueError("Only the founder can close the store")

    store.is_active = False
    store.save()

    return {"message": "Store closed successfully"}


@router.put("stores/{store_id}/reopen_store")
def reopen_store(request, payload: RoleSchemaIn):
    store = get_object_or_404(Store, pk=payload.store_id)
    owner = get_object_or_404(Owner, user_id=payload.user_id, store=store)
    if not owner.is_founder:
        raise ValueError("Only the founder can reopen the store")

    store.is_active = True
    store.save()

    return {"message": "Store reopened successfully"}


@router.get("/stores/{store_id}", response=List[OwnerSchemaOut])
def get_owners(request, payload: RoleSchemaIn):
    store = get_object_or_404(Store, pk=payload.store_id)
    if not Owner.objects.filter(user_id=payload.user_id, store=store).exists():
        raise ValueError("User is not an owner of the store")

    owners = Owner.objects.filter(store=store)

    return owners

@router.post("/stores/{store_id}/add_purchase_policy")
def add_purchase_policy(request, role: RoleSchemaIn, payload: PurchasePolicySchemaIn):
    store = get_object_or_404(Store, pk=role.store_id)
    if not Owner.objects.filter(user_id=role.user_id, store=store).exists():
        if not Manager.objects.filter(user_id=role.user_id, store=store).exists():
            raise ValueError("User is not an owner or manager of the store")
        manager = get_object_or_404(Manager, user_id=role.user_id, store=store)
        manager_permissions = get_object_or_404(ManagerPermission, manager=manager)
        if not manager_permissions.can_add_purchase_policy:
            raise ValueError("Manager does not have permission to add purchase policy")

    policy, _ = PurchasePolicy.objects.create(
        store=store,
        defaults=payload.dict()
    )

    return {"message": "Purchase policy added successfully"}

@router.delete("/stores/{store_id}/remove_purchase_policy")
def remove_purchase_policy(request, role: RoleSchemaIn):
    store = get_object_or_404(Store, pk=role.store_id)
    if not Owner.objects.filter(user_id=role.user_id, store=store).exists():
        if not Manager.objects.filter(user_id=role.user_id, store=store).exists():
            raise ValueError("User is not an owner or manager of the store")
        manager = get_object_or_404(Manager, user_id=role.user_id, store=store)
        manager_permissions = get_object_or_404(ManagerPermission, manager=manager)
        if not manager_permissions.can_remove_purchase_policy:
            raise ValueError("Manager does not have permission to remove purchase policy")

    policy = get_object_or_404(PurchasePolicy, store=store)
    policy.delete()

    return {"message": "Purchase policy removed successfully"}

# @router.post("/stores/{store_id}/change_purchase_policy")
# def change_purchase_policy(request, role: RoleSchemaIn, payload: PurchasePolicySchemaIn):
#     store = get_object_or_404(Store, pk=role.store_id)
#     if not Owner.objects.filter(user_id=role.user_id, store=store).exists():
#         if not Manager.objects.filter(user_id=role.user_id, store=store).exists():
#             raise ValueError("User is not an owner or manager of the store")
#         manager = get_object_or_404(Manager, user_id=role.user_id, store=store)
#         manager_permissions = get_object_or_404(ManagerPermission, manager=manager)
#         if not manager_permissions.can_change_purchase_policy:
#             raise ValueError("Manager does not have permission to change purchase policy")
#
#     policy, _ = PurchasePolicy.objects.update_or_create(
#         store=store,
#         defaults=payload.dict()
#     )
#
#     return {"message": "Purchase policy updated successfully"}


@router.post("/stores/{store_id}/add_discount_policy")
def change_discount_policy(request, role: RoleSchemaIn, payload: DiscountPolicySchemaIn):
    store = get_object_or_404(Store, pk=role.store_id)
    if not Owner.objects.filter(user_id=role.user_id, store=store).exists():
        if not Manager.objects.filter(user_id=role.user_id, store=store).exists():
            raise ValueError("User is not an owner or manager of the store")
        manager = get_object_or_404(Manager, user_id=role.user_id, store=store)
        manager_permissions = get_object_or_404(ManagerPermission, manager=manager)
        if not manager_permissions.can_add_discount_policy:
            raise ValueError("Manager does not have permission to change discount policy")
    if DiscountPolicy.objects.filter(store=store, min_items=payload.min_items, min_price=payload.min_price).exists():
        raise ValueError("Discount policy with these parameters already exists")
    policy, _ = DiscountPolicy.objects.create(
        store=store,
        defaults=payload.dict()
    )

    return {"message": "Discount policy added successfully"}

@router.delete("/stores/{store_id}/remove_discount_policy")
def remove_discount_policy(request, role: RoleSchemaIn):
    store = get_object_or_404(Store, pk=role.store_id)
    if not Owner.objects.filter(user_id=role.user_id, store=store).exists():
        if not Manager.objects.filter(user_id=role.user_id, store=store).exists():
            raise ValueError("User is not an owner or manager of the store")
        manager = get_object_or_404(Manager, user_id=role.user_id, store=store)
        manager_permissions = get_object_or_404(ManagerPermission, manager=manager)
        if not manager_permissions.can_remove_discount_policy:
            raise ValueError("Manager does not have permission to change discount policy")

    policy = get_object_or_404(DiscountPolicy, store=store)
    policy.delete()

    return {"message": "Discount policy removed successfully"}

# not sure if editing discount policies is needed, can just delete and add new ones
#
# @router.put("/stores/{store_id}/edit_discount_policy")
# def edit_discount_policy(request, role: RoleSchemaIn, payload: DiscountPolicySchemaIn):
#     store = get_object_or_404(Store, pk=role.store_id)
#     if not Owner.objects.filter(user_id=role.user_id, store=store).exists():
#         if not Manager.objects.filter(user_id=role.user_id, store=store).exists():
#             raise ValueError("User is not an owner or manager of the store")
#         manager = get_object_or_404(Manager, user_id=role.user_id, store=store)
#         manager_permissions = get_object_or_404(ManagerPermission, manager=manager)
#         if not manager_permissions.can_change_discount_policy:
#             raise ValueError("Manager does not have permission to change discount policy")
#
#     policy = get_object_or_404(DiscountPolicy, store=store)
#     policy.update(**payload.dict())
#
#     return {"message": "Discount policy edited successfully"}
#

@router.post("/stores/{store_id}/add_product")
def add_product(request, role: RoleSchemaIn, payload: StoreProductSchemaIn):
    store = get_object_or_404(Store, pk=role.store_id)
    if not Owner.objects.filter(user_id=role.user_id, store=store).exists():
        if not Manager.objects.filter(user_id=role.user_id, store=store).exists():
            raise ValueError("User is not an owner or manager of the store")
        manager = get_object_or_404(Manager, user_id=role.user_id, store=store)
        manager_permissions = get_object_or_404(ManagerPermission, manager=manager)
        if not manager_permissions.can_add_product:
            raise ValueError("Manager does not have permission to add product")

    all_products = StoreProduct.objects.filter(store=store)
    if payload.name in all_products.values_list('name', flat=True):
        raise ValueError("Product with this name already exists in the store")

    product = StoreProduct.objects.create(
        store=store,
        defaults=payload.dict()
    )

    return {"message": "Product added successfully"}


@router.delete("/stores/{store_id}/remove_product")
def remove_product(request, role: RoleSchemaIn, product_name: str):
    store = get_object_or_404(Store, pk=role.store_id)
    if not Owner.objects.filter(user_id=role.user_id, store=store).exists():
        if not Manager.objects.filter(user_id=role.user_id, store=store).exists():
            raise ValueError("User is not an owner or manager of the store")
        manager = get_object_or_404(Manager, user_id=role.user_id, store=store)
        manager_permissions = get_object_or_404(ManagerPermission, manager=manager)
        if not manager_permissions.can_delete_product:
            raise ValueError("Manager does not have permission to delete product")

    product = get_object_or_404(StoreProduct, store=store, name=product_name)
    product.delete()

    return {"message": "Product removed successfully"}


@router.put("/stores/{store_id}/edit_product")
def edit_product(request, role: RoleSchemaIn, payload: StoreProductSchemaIn):
    store = get_object_or_404(Store, pk=role.store_id)
    if not Owner.objects.filter(user_id=role.user_id, store=store).exists():
        if not Manager.objects.filter(user_id=role.user_id, store=store).exists():
            raise ValueError("User is not an owner or manager of the store")
        manager = get_object_or_404(Manager, user_id=role.user_id, store=store)
        manager_permissions = get_object_or_404(ManagerPermission, manager=manager)
        if not manager_permissions.can_edit_product:
            raise ValueError("Manager does not have permission to edit product")

    product = get_object_or_404(StoreProduct, store=store, name=payload.name)
    if payload.quantity <= 0:
        raise ValueError("Product quantity cannot be negative, if you wish to set quantity to 0, remove the product "
                         "instead")

    product.update(**payload.dict())

    return {"message": "Product edited successfully"}


@router.get("/stores/{store_id}/get_products", response=List[StoreProductSchemaOut])
def get_products(request, role: RoleSchemaIn):
    store = get_object_or_404(Store, pk=role.store_id)
    if not Owner.objects.filter(user_id=role.user_id, store=store).exists() and not store.is_active:
        raise ValueError("User is not an owner of the store and the store is closed")

    products = StoreProduct.objects.filter(store=store)

    return products


@router.put("/stores/{store_id}/purchase_product")
def purchase_product(request, payload: List[PurchaseStoreProductSchema]):
    store = get_object_or_404(Store, pk=payload[0].store_id)
    #product = get_object_or_404(StoreProduct, store=store, name=payload.product_name)
    store_purchase_policy = get_object_or_404(PurchasePolicy, store=store)
    total_items = sum([item.quantity for item in payload])
    products = [get_object_or_404(StoreProduct, store=store, name=item.product_name) for item in payload]
    total_price = sum([product.initial_price * item.quantity for product, item in zip(products, payload)])
    if store_purchase_policy.max_items_per_purchase and total_items > store_purchase_policy.max_items_per_purchase:
        raise ValueError("Total items exceeds the maximum items per purchase limit")
    if store_purchase_policy.min_items_per_purchase and total_items < store_purchase_policy.min_items_per_purchase:
        raise ValueError("Total items is less than the minimum items per purchase limit")

    store_discount_policy = get_object_or_404(DiscountPolicy, store=store)
    if (store_discount_policy.min_items and total_items >= store_discount_policy.min_items) and (
            store_discount_policy.min_price and total_price >= store_discount_policy.min_price):
        total_price = total_price * 0.9  # 10% discount - assume for now that discount is always 10%

    for product, item in zip(products, payload):
        if product.quantity < item.quantity:
            raise ValueError(f"Insufficient quantity of {product.name} in store")
        product.quantity -= item.quantity
        if product.quantity == 0:
            product.delete()
        else:
            product.save()

    return {"message": "Products purchased successfully", "total_price": total_price}



