from http.client import HTTPException
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
def get_store(request, store_id: int):
    return get_object_or_404(Store, pk=store_id)

# @router.get("/stores/{store_id}", response=StoreSchemaOut)
# async def get_store(request, store_id: int):
#     return await aget_object_or_404(Store, pk=store_id)


@router.post("/stores")
def create_store(request, payload: StoreSchemaIn, user_id: int):
    if Store.objects.filter(name=payload.name).exists():
        raise HTTPException(403, "Store with this name already exists")
    store = Store.objects.create(**payload.dict(), is_active=True)
    Owner.objects.create(
        user_id=user_id,
        store=store,
        is_founder=True
    )
    return {"store_id": store.id}

# @router.post("/stores")
# async def create_store(request, payload: StoreSchemaIn, user_id: int):
#     if Store.objects.filter(name=payload.name).exists():
#         raise HTTPException(403, "Store with this name already exists")
#     store = await Store.objects.acreate(**payload.dict(), is_active=True)
#     await Owner.objects.acreate(
#         user_id=user_id,
#         store=store,
#         is_founder=True
#     )
#     return {"store_id": store.id}


@router.get("/stores", response=List[StoreSchemaOut])
def get_stores(request):
    return Store.objects.all()

# @router.get("/stores", response=List[StoreSchemaOut])
# async def get_stores(request):
#     return await Store.objects.all()


@router.post("/stores/{store_id}/assign_owner")
def assign_owner(request, payload: OwnerSchemaIn):
    store = get_object_or_404(Store, pk=payload.store_id)
    assigning_owner = get_object_or_404(Owner, user_id=payload.assigned_by, store=store)
    if Owner.objects.filter(user_id=payload.user_id, store=store).exists():
        raise HTTPException(400, "User is already an owner")


    owner = Owner.objects.create(
        user_id=payload.user_id,
        assigned_by=assigning_owner,
        store=store,
        is_founder=False
    )
    return {"message": "Owner assigned successfully"}

# @router.post("/stores/{store_id}/assign_owner")
# async def assign_owner(request, payload: OwnerSchemaIn):
#     store = await aget_object_or_404(Store, pk=payload.store_id)
#     assigning_owner = await aget_object_or_404(Owner, user_id=payload.assigned_by, store=store)
#     if await Owner.objects.filter(user_id=payload.user_id, store=store).exists():
#         raise HTTPException(400, "User is already an owner")
#
#
#     owner = await Owner.objects.acreate(
#         user_id=payload.user_id,
#         assigned_by=assigning_owner,
#         store=store,
#         is_founder=payload.is_founder
#     )
#     return {"message": "Owner assigned successfully"}


# @router.delete("/stores/{store_id}/remove_owner")
# async def remove_owner(request, payload: OwnerSchemaIn):
#     store = await aget_object_or_404(Store, pk=payload.store_id)
#     removing_owner = await aget_object_or_404(Owner, user_id=payload.removed_by, store=store)
#     removed_owner = await aget_object_or_404(Owner, user_id=payload.user_id, store=store)
#
#     if removed_owner.assigned_by != removing_owner:
#         raise HTTPException(403, "Owner can only be removed by the owner who assigned them")
#
#     await removed_owner.adelete()
#     return {"message": "Owner removed success"}


@router.delete("/stores/{store_id}/remove_owner")
def remove_owner(request, payload: OwnerSchemaIn):
    store = get_object_or_404(Store, pk=payload.store_id)
    removing_owner = get_object_or_404(Owner, user_id=payload.removed_by, store=store)
    removed_owner = get_object_or_404(Owner, user_id=payload.user_id, store=store)

    if removed_owner.assigned_by != removing_owner:
        raise HTTPException(403, "Owner can only be removed by the owner who assigned them")

    removed_owner.delete()
    return {"message": "Owner removed successfully"}


@router.delete("/stores/{store_id}/leave_ownership")
def leave_ownership(request, payload: OwnerSchemaIn):
    store = get_object_or_404(Store, pk=payload.store_id)
    owner = get_object_or_404(Owner, user_id=payload.user_id, store=store)
    if owner.is_founder:
        raise HTTPException(400, "Founder cannot leave ownership")

    owner.delete()
    return {"message": "Ownership left successfully"}


@router.post("/stores/{store_id}/assign_manager")
def assign_manager(request, payload: ManagerSchemaIn):
    store = get_object_or_404(Store, pk=payload.store_id)
    assigning_owner = get_object_or_404(Owner, user_id=payload.assigned_by, store=store)
    if Manager.objects.filter(user_id=payload.user_id, store=store).exists():
        raise HTTPException(400, "User is already a manager")
    elif Owner.objects.filter(user_id=payload.user_id, store=store).exists():
        raise HTTPException(400, "User is already an owner")

        # Check if the assigning user is an owner
    if not Owner.objects.filter(user_id=payload.assigned_by, store=store).exists():
        raise HTTPException(403, "Only owners can assign managers")

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
        raise HTTPException(403, "Manager can only be removed by the owner who assigned them")

    removed_manager.delete()
    return {"message": "Manager removed successfully"}


@router.post("/stores/{store_id}/change_manager_permissions")
def assign_manager_permissions(request, payload: ManagerPermissionSchemaIn, manager: RoleSchemaIn,
                               assigning_owner_id: int):
    store = get_object_or_404(Store, pk=manager.store_id)
    manager = get_object_or_404(Manager, user_id=manager.user_id, store=store)
    if assigning_owner_id != manager.assigned_by.user_id:
        raise HTTPException(403, "Only assigning owner can assign permissions")
    try:
        existing_permission, _ = ManagerPermission.objects.update_or_create(
            manager=manager,
            defaults=payload.dict()
        )
    except Exception as e:
        raise HTTPException(500, f"Error assigning permissions: {str(e)}")

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
        raise HTTPException(403, "Only the founder can close the store")

    store.is_active = False
    store.save()

    return {"message": "Store closed successfully"}


@router.put("stores/{store_id}/reopen_store")
def reopen_store(request, payload: RoleSchemaIn):
    store = get_object_or_404(Store, pk=payload.store_id)
    owner = get_object_or_404(Owner, user_id=payload.user_id, store=store)
    if not owner.is_founder:
        raise HTTPException(403, "Only the founder can reopen the store")

    store.is_active = True
    store.save()

    return {"message": "Store reopened successfully"}


@router.get("/stores/{store_id}", response=List[OwnerSchemaOut])
def get_owners(request, payload: RoleSchemaIn):
    store = get_object_or_404(Store, pk=payload.store_id)
    if not Owner.objects.filter(user_id=payload.user_id, store=store).exists():
        raise HTTPException(403, "User is not an owner of the store")

    owners = Owner.objects.filter(store=store)

    return owners


@router.post("/stores/{store_id}/add_purchase_policy")
def add_purchase_policy(request, role: RoleSchemaIn, payload: PurchasePolicySchemaIn):
    store = get_object_or_404(Store, pk=role.store_id)

    # Check if the user is an owner or manager of the store
    if not Owner.objects.filter(user_id=role.user_id, store=store).exists():
        if not Manager.objects.filter(user_id=role.user_id, store=store).exists():
            raise HTTPException(403, "User is not an owner or manager of the store")

        manager = get_object_or_404(Manager, user_id=role.user_id, store=store)
        manager_permissions = get_object_or_404(ManagerPermission, manager=manager)
        if not manager_permissions.can_add_purchase_policy:
            raise HTTPException(403, "Manager does not have permission to add purchase policy")

    # Check if a purchase policy already exists for the store
    if PurchasePolicy.objects.filter(store=store).exists():
        raise HTTPException(400, "Purchase policy already exists for the store")

    policy = PurchasePolicy.objects.create(
        store=store,
        **payload.dict()
    )

    return {"message": "Purchase policy added successfully"}


@router.delete("/stores/{store_id}/remove_purchase_policy")
def remove_purchase_policy(request, store_id: int, role: RoleSchemaIn):
    store = get_object_or_404(Store, pk=store_id)

    # Check if the user is an owner or manager of the store
    if not Owner.objects.filter(user_id=role.user_id, store=store).exists():
        if not Manager.objects.filter(user_id=role.user_id, store=store).exists():
            raise HTTPException(403, "User is not an owner or manager of the store")

        manager = get_object_or_404(Manager, user_id=role.user_id, store=store)
        manager_permissions = get_object_or_404(ManagerPermission, manager=manager)
        if not manager_permissions.can_remove_purchase_policy:
            raise HTTPException(403, "Manager does not have permission to remove purchase policy")

    # Check if a purchase policy exists for the store
    try:
        policy = PurchasePolicy.objects.get(store=store)
    except PurchasePolicy.DoesNotExist:
        raise HTTPException(404, "Purchase policy not found for the store")

    # Delete the purchase policy
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

    # Check if the user is an owner or manager of the store
    if not Owner.objects.filter(user_id=role.user_id, store=store).exists():
        if not Manager.objects.filter(user_id=role.user_id, store=store).exists():
            raise HTTPException(403, "User is not an owner or manager of the store")

        manager = get_object_or_404(Manager, user_id=role.user_id, store=store)
        manager_permissions = get_object_or_404(ManagerPermission, manager=manager)
        if not manager_permissions.can_add_discount_policy:
            raise HTTPException(403, "Manager does not have permission to change discount policy")

    # Check if a discount policy with the same parameters already exists for the store
    if DiscountPolicy.objects.filter(store=store, min_items=payload.min_items, min_price=payload.min_price).exists():
        raise HTTPException(400, "Discount policy with these parameters already exists")

    policy = DiscountPolicy.objects.create(
        store=store,
        **payload.dict()
    )

    return {"message": "Discount policy added successfully"}


@router.delete("/stores/{store_id}/remove_discount_policy")
def remove_discount_policy(request, role: RoleSchemaIn, payload: DiscountPolicySchemaIn):
    store = get_object_or_404(Store, pk=role.store_id)

    # Check if the user is an owner or manager of the store
    if not Owner.objects.filter(user_id=role.user_id, store=store).exists():
        if not Manager.objects.filter(user_id=role.user_id, store=store).exists():
            raise HTTPException(403, "User is not an owner or manager of the store")

        manager = get_object_or_404(Manager, user_id=role.user_id, store=store)
        manager_permissions = get_object_or_404(ManagerPermission, manager=manager)
        if not manager_permissions.can_remove_discount_policy:
            raise HTTPException(403, "Manager does not have permission to change discount policy")

    # Check if a discount policy exists for the store
    try:
        policy = DiscountPolicy.objects.get(store=store, min_items=payload.min_items, min_price=payload.min_price)
    except DiscountPolicy.DoesNotExist:
        raise HTTPException(404, "Discount policy not found for the store")

    # Delete the discount policy
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
            raise HTTPException(403, "User is not an owner or manager of the store")

        manager = get_object_or_404(Manager, user_id=role.user_id, store=store)
        manager_permissions = get_object_or_404(ManagerPermission, manager=manager)
        if not manager_permissions.can_add_product:
            raise HTTPException(403, "Manager does not have permission to add product")

    all_products = StoreProduct.objects.filter(store=store)
    if payload.name in all_products.values_list('name', flat=True):
        raise HTTPException(400, "Product with this name already exists in the store")
    if payload.quantity <= 0:
        raise HTTPException(400, "Product quantity cannot be 0 or negative")
    if payload.initial_price <= 0:
        raise HTTPException(400, "Product price cannot be 0 or negative")

    product = StoreProduct.objects.create(store=store, **payload.dict())

    return {"message": "Product added successfully"}


@router.delete("/stores/{store_id}/remove_product")
def remove_product(request, store_id: int, role: RoleSchemaIn, product_name: str):
    store = get_object_or_404(Store, pk=store_id)

    # Check if the user is an owner or manager of the store
    if not Owner.objects.filter(user_id=role.user_id, store=store).exists():
        if not Manager.objects.filter(user_id=role.user_id, store=store).exists():
            raise HTTPException(403, "User is not an owner or manager of the store")

        manager = get_object_or_404(Manager, user_id=role.user_id, store=store)
        manager_permissions = get_object_or_404(ManagerPermission, manager=manager)
        if not manager_permissions.can_delete_product:
            raise HTTPException(403, "Manager does not have permission to delete product")

    # Check if the product exists
    product = get_object_or_404(StoreProduct, store=store, name=product_name)

    # Delete the product
    product.delete()

    return {"message": "Product removed successfully"}


@router.put("/stores/{store_id}/edit_product")
def edit_product(request, store_id: int, role: RoleSchemaIn, payload: StoreProductSchemaIn):
    store = get_object_or_404(Store, pk=store_id)

    # Check if the user is an owner or manager of the store
    if not Owner.objects.filter(user_id=role.user_id, store=store).exists():
        if not Manager.objects.filter(user_id=role.user_id, store=store).exists():
            raise HTTPException(403, "User is not an owner or manager of the store")

        manager = get_object_or_404(Manager, user_id=role.user_id, store=store)
        manager_permissions = get_object_or_404(ManagerPermission, manager=manager)
        if not manager_permissions.can_edit_product:
            raise HTTPException(403, "Manager does not have permission to edit product")

    # Get the product to edit
    product = get_object_or_404(StoreProduct, store=store, name=payload.name)

    # Validate payload
    if payload.quantity <= 0:
        raise HTTPException(400, "Product quantity cannot be negative. To remove the product, delete it instead.")

    # Update the product attributes
    product.quantity = payload.quantity
    product.initial_price = payload.initial_price
    product.save()

    return {"message": "Product edited successfully"}


@router.get("/stores/{store_id}/get_products", response=List[StoreProductSchemaOut])
def get_products(request, store_id: int, role: RoleSchemaIn):
    store = get_object_or_404(Store, pk=store_id)
    if not Owner.objects.filter(user_id=role.user_id, store=store).exists() and not store.is_active:
        raise HTTPException(403, "User is not an owner of the store and the store is closed")

    # Get products for the store
    products = StoreProduct.objects.filter(store=store)

    products = StoreProduct.objects.filter(store=store)

    return products


@router.put("/stores/{store_id}/purchase_product")
def purchase_product(request, store_id: int, payload: List[PurchaseStoreProductSchema]):
    store = get_object_or_404(Store, pk=store_id)

    total_items = sum(item.quantity for item in payload)
    total_price = sum(item.product_price * item.quantity for item in payload)

    # Check purchase policy limits
    store_purchase_policy = get_object_or_404(PurchasePolicy, store=store)
    if store_purchase_policy.max_items_per_purchase and total_items > store_purchase_policy.max_items_per_purchase:
        raise HTTPException(400, "Total items exceeds the maximum items per purchase limit")
    if store_purchase_policy.min_items_per_purchase and total_items < store_purchase_policy.min_items_per_purchase:
        raise HTTPException(400, "Total items is less than the minimum items per purchase limit")

    # Apply discount policy
    store_discount_policy = get_object_or_404(DiscountPolicy, store=store)
    if (store_discount_policy.min_items and total_items >= store_discount_policy.min_items) and (
            store_discount_policy.min_price and total_price >= store_discount_policy.min_price):
        total_price *= 0.9  # Apply 10% discount

    for item in payload:
        product = get_object_or_404(StoreProduct, store=store, name=item.product_name)
        if product.quantity < item.quantity:
            raise HTTPException(400, f"Insufficient quantity of {product.name} in store")
        product.quantity -= item.quantity
        if product.quantity == 0:
            product.delete()
        else:
            product.save()

    return {"message": "Products purchased successfully", "total_price": total_price}
