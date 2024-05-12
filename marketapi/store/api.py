from django.http import HttpResponse
from ninja import Router

from models import Store, Owner, Manager, ManagerPermission
from schemas import StoreSchemaIn, StoreSchemaOut, OwnerSchema, ManagerPermissionSchema
from django.shortcuts import get_object_or_404

router = Router()


@router.get("/store/{store_id}", response=StoreSchemaOut)
def get_store(request, store_id: int):
    return get_object_or_404(Store, pk=store_id)


@router.post("/store")
def create_store(request, payload: StoreSchemaIn):
    store = Store.objects.create(**payload.dict())
    return {"id": store.id}


@router.post("/stores/{store_id}/assign_owner")
def assign_owner(request, store_id: int, assigning_owner_id: int, assigned_user_id: int):
    store = get_object_or_404(Store, pk=store_id)

    #check that the assining owner is at all an owner of the store
    assigning_owner = get_object_or_404(Owner, user_id=assigning_owner_id, store=store)
    if Owner.objects.filter(user_id=assigned_user_id, store=store).exists():
        raise ValueError("User is already an owner")

    owner = Owner.objects.create(
        user_id=assigned_user_id,
        assigned_by=assigning_owner,
        store=store,
        is_founder=False
    )

    return {"message": "Owner assigned successfully"}


@router.delete("/stores/{store_id}/remove_owner")
def remove_owner(request, store_id: int, removing_owner_id: int, removed_user_id: int):
    store = get_object_or_404(Store, pk=store_id)
    removing_owner = get_object_or_404(Owner, user_id=removing_owner_id, store=store)
    removed_owner = get_object_or_404(Owner, user_id=removed_user_id, store=store)

    if removed_owner.assigned_by != removing_owner:
        raise ValueError("Owner can only be removed by the owner who assigned them")

    removed_owner.delete()

    return {"message": "Owner removed successfully"}


@router.delete("/stores/{store_id}/leave_ownership")
def leave_ownership(request, store_id: int, owner_id: int):
    store = get_object_or_404(Store, pk=store_id)
    owner = get_object_or_404(Owner, user_id=owner_id, store=store)

    if owner.is_founder:
        raise ValueError("Founder cannot leave ownership")

    owner.delete()

    return {"message": "Ownership left successfully"}


@router.post("/stores/{store_id}/assign_manager")
def assign_manager(request, store_id: int, assigning_owner_id: int, assigned_user_id: int):
    store = get_object_or_404(Store, pk=store_id)
    assigning_owner = get_object_or_404(Owner, user_id=assigning_owner_id, store=store)

    if Manager.objects.filter(user_id=assigned_user_id, store=store).exists():
        raise ValueError("User is already a manager")
    elif Owner.objects.filter(user_id=assigned_user_id, store=store).exists():
        raise ValueError("User is already an owner")

    manager = Manager.objects.create(
        user_id=assigned_user_id,
        assigned_by=assigning_owner,
        store=store
    )

    return {"message": "Manager assigned successfully"}


@router.delete("/stores/{store_id}/remove_manager")
def remove_manager(request, store_id: int, removing_owner_id: int, removed_user_id: int):
    store = get_object_or_404(Store, pk=store_id)
    removing_owner = get_object_or_404(Owner, user_id=removing_owner_id, store=store)
    removed_manager = get_object_or_404(Manager, user_id=removed_user_id, store=store)

    if removed_manager.assigned_by != removing_owner:
        raise ValueError("Manager can only be removed by the owner who assigned them")

    removed_manager.delete()

    return {"message": "Manager removed successfully"}


@router.post("/stores/{store_id}/assign_manager_permissions")
def assign_manager_permissions(request, payload: ManagerPermissionSchema, store_id: int, manager_id: int,
                               assigning_owner_id: int):
    store = get_object_or_404(Store, pk=store_id)
    manager = get_object_or_404(Manager, pk=payload.manager_id, store=store)
    assigning_owner = get_object_or_404(Owner, user_id=assigning_owner_id, store=store)
    payload = payload.dict(Exclude={"manager"})

    try:
        existing_permission, _ = ManagerPermission.objects.update_or_create(
            manager=manager,
            **payload.dict()
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
def close_store(request, store_id: int, owner_id: int):
    store = get_object_or_404(Store, pk=store_id)
    owner = get_object_or_404(Owner, user_id=owner_id, store=store)
    if not owner.is_founder:
        raise ValueError("Only the founder can close the store")

    store.is_active = False
    store.save()

    return {"message": "Store closed successfully"}


@router.put("stores/{store_id}/reopen_store")
def reopen_store(request, store_id: int, owner_id: int):
    store = get_object_or_404(Store, pk=store_id)
    owner = get_object_or_404(Owner, user_id=owner_id, store=store)
    if not owner.is_founder:
        raise ValueError("Only the founder can reopen the store")

    store.is_active = True
    store.save()

    return {"message": "Store reopened successfully"}

@router.get("/stores/{store_id}/get_owners")
def get_owners(request, store_id: int, owner_id: int):
    store = get_object_or_404(Store, pk=store_id)

    if not Owner.objects.filter(user_id=owner_id, store=store).exists():
        raise ValueError("User is not an owner of the store")

    owners = Owner.objects.filter(store=store)

    return owners


