import json
import operator
from functools import reduce
from typing import List, Union

import redis
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, connection
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError
from django.http import Http404
import random

from .discount import (
    SimpleDiscountClass,
    ConditionalDiscountClass,
    CompositeDiscountClass,
)
from .models import (
    Store,
    Owner,
    Manager,
    ManagerPermission,
    StoreProduct,
    SimpleDiscount,
    ConditionalDiscount,
    CompositeDiscount,
    DiscountBase,
    Condition,
    PurchasePolicyBase,
    SimplePurchasePolicy,
    ConditionalPurchasePolicy,
    CompositePurchasePolicy,
    Bid,
    Role,
)
from .purchasePolicy import (
    SimplePurchasePolicyClass,
    ConditionalPurchasePolicyClass,
    CompositePurchasePolicyClass,
)
from .schemas import (
    StoreSchemaIn,
    OwnerSchemaIn,
    ManagerPermissionSchemaIn,
    SimplePurchasePolicySchemaIn,
    ConditionalPurchasePolicySchemaIn,
    CompositePurchasePolicySchemaIn,
    StoreProductSchemaIn,
    ManagerSchemaIn,
    RoleSchemaIn,
    PurchaseStoreProductSchema,
    RemoveOwnerSchemaIn,
    RemoveManagerSchemaIn,
    SimpleDiscountSchemaIn,
    CompositeDiscountSchemaIn,
    ConditionalDiscountSchemaIn,
    RemoveDiscountSchemaIn,
    ConditionalDiscountSchemaOut,
    CompositeDiscountSchemaOut,
    FilterSearchSchema,
    SearchSchema,
    RemovePurchasePolicySchemaIn,
    BidSchemaIn,
    DecisionBidSchemaIn,
    MakePurchaseOnBidSchemaIn,
    ConditionSchema,
    MakePurchaseOnBidSchemaIn,
    GetConditionsSchemaIn, GetBidsOnProductSchema,
)

router = Router()
store_lock = hash("store_lock")

from users.usercontroller import UserController

uc = UserController()


def get_list_from_string(conditions):
    jsonDec = json.decoder.JSONDecoder()
    return jsonDec.decode(conditions)


def get_keys_by_prefix(prefix):
    redis_client = redis.Redis(host='redis', port=6379, db=0)
    keys = redis_client.keys(f":1:{prefix}*")
    filtered_keys = [key.decode('utf-8').replace(":1:", "") for key in keys]
    return filtered_keys


def get_or_set_cache(key, model, **kwargs):
    obj = cache.get(key)
    if obj is None:
        obj = get_object_or_404(model, **kwargs)
        cache.set(key, obj)
    return obj


################
# Rules of thumb when using cache #
# 1. Always check cache first before accessing the db
# 2. when doing a get operation to the cache - if its not there make sure to set it
# 3. when accessing the db when its unavoidable, make sure to update the cache, but make it smart - use signals
# so that the cache is updated when the db is updated and you dont have to manually update the cache (post_init, post_save, post_delete)


class StoreController:
    def get_store(self, request, store_id: int):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                cache_key_store = f"store_{store_id}"
                store = get_or_set_cache(cache_key_store, Store, pk=store_id)

        return store

    def create_store(self, request, payload: StoreSchemaIn, user_id: int):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock(%s);", [store_lock])
                all_store_keys = get_keys_by_prefix('store_')
                #print(all_store_keys)
                for key in all_store_keys:
                    #print(key)
                    store = cache.get(key)
                    if store.name == payload.name:
                        raise HttpError(403, "Store with this name already exists")
                if Store.objects.filter(
                        name=payload.name).exists():  #still need to check the database because cache may not be updated
                    raise HttpError(403, "Store with this name already exists")
                store = Store.objects.create(**payload.dict(), is_active=True)
                # cache_key_store = f"store_{store.id}"
                # cache.set(cache_key_store, store)
                owner = Owner.objects.create(user_id=user_id, store=store, is_founder=True)
                # cache_key_owner = f"owner_{store.id}_{user_id}"
                # cache.set(cache_key_owner, owner)

        uc.send_notification(
            store.name, user_id, f"Store {store.name} created successfully"
        )
        return {"store_id": store.id}

    def get_stores(self, request):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                stores = Store.objects.all()  #to get stores we cant use cache because we need to get all stores
                cache.set_many({f"store_{store.id}": store for store in stores})  #but we will save to cache
                return stores

    def assign_owner(self, request, payload: OwnerSchemaIn):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                cache_key_store = f"store_{payload.store_id}"
                store = get_or_set_cache(cache_key_store, Store, pk=payload.store_id)
                managing_lock_id = f"{store.pk}_managing_lock"
                cursor.execute(
                    f"SELECT pg_advisory_xact_lock({hash(managing_lock_id)});"
                )
                cache_key_assigning_owner = f"owner_{store.id}_{payload.assigned_by}"
                assigning_owner = get_or_set_cache(cache_key_assigning_owner, Owner, user_id=payload.assigned_by,
                                                   store=store)

                cache_key_check_owner = f"owner_{store.id}_{payload.user_id}"
                check_owner = cache.get(cache_key_check_owner)
                if check_owner is not None:
                    raise HttpError(400, "User is already an owner")
                if Owner.objects.filter(user_id=payload.user_id,
                                        store=store).exists():  #we still have to check the database because cache may not be updated
                    cache.set(cache_key_check_owner, Owner.objects.get(user_id=payload.user_id,
                                                                       store=store))  #because we didnt have it in the cache
                    raise HttpError(400, "User is already an owner")

                cache_key_check_manager = f"manager_{store.id}_{payload.user_id}"
                check_manager = cache.get(cache_key_check_manager)
                if check_manager is not None:
                    raise HttpError(400, "User is already a manager")
                if Manager.objects.filter(user_id=payload.user_id, store=store).exists():
                    cache.set(cache_key_check_manager, Manager.objects.get(user_id=payload.user_id, store=store))
                    raise HttpError(400, "User is already a manager")

                owner = Owner.objects.create(
                    user_id=payload.user_id,
                    assigned_by=assigning_owner,
                    store=store,
                    is_founder=False,
                )
        uc.send_notification(
            store.name,
            payload.user_id,
            f"You have been assigned as an owner of {store.name}",
        )
        return {"message": "Owner assigned successfully"}

    def remove_owner(self, request, payload: RemoveOwnerSchemaIn):

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                cache_key_store = f"store_{payload.store_id}"
                store = get_or_set_cache(cache_key_store, Store, pk=payload.store_id)
                managing_lock_id = f"{store.pk}_managing_lock"
                cursor.execute(
                    f"SELECT pg_advisory_xact_lock({hash(managing_lock_id)});"
                )
                cache_key_removing_owner = f"owner_{store.id}_{payload.removed_by}"
                removing_owner = get_or_set_cache(cache_key_removing_owner, Owner, user_id=payload.removed_by,
                                                  store=store)
                cache_key_removed_owner = f"owner_{store.id}_{payload.user_id}"
                removed_owner = get_or_set_cache(cache_key_removed_owner, Owner, user_id=payload.user_id, store=store)
                if removed_owner.assigned_by != removing_owner:
                    raise HttpError(
                        403, "Owner can only be removed by the owner who assigned them"
                    )

                removed_owner.delete()  #cache is deleted upon signal to db

        uc.send_notification(
            store.name,
            payload.user_id,
            f"You have been removed as an owner of {store.name}",
        )
        return {"message": "Owner removed successfully"}

    def leave_ownership(self, request, payload: RoleSchemaIn):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{payload.store_id}", Store, pk=payload.store_id)
                managing_lock_id = f"{store.pk}_managing_lock"
                cursor.execute(
                    f"SELECT pg_advisory_xact_lock({hash(managing_lock_id)});"
                )
                cache_key_owner = f"owner_{store.id}_{payload.user_id}"
                owner = get_or_set_cache(cache_key_owner, Owner, user_id=payload.user_id, store=store)
                if owner.is_founder:
                    raise HttpError(400, "Founder cannot leave ownership")

                owner.delete()
        uc.send_notification(
            store.name, payload.user_id, f"You have left ownership of {store.name}"
        )
        return {"message": "Ownership left successfully"}

    def assign_manager(self, request, payload: ManagerSchemaIn):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{payload.store_id}", Store, pk=payload.store_id)
                managing_lock_id = hash(f"{store.pk}_managing_lock")
                # Acquire an advisory lock on the store
                cursor.execute("SELECT pg_advisory_xact_lock(%s);", [managing_lock_id])
                assigning_owner = get_or_set_cache(f"owner_{store.id}_{payload.assigned_by}", Owner,
                                                   user_id=payload.assigned_by, store=store)
                cache_key_check_manager = f"manager_{store.id}_{payload.user_id}"
                check_manager = cache.get(cache_key_check_manager)
                if check_manager is not None:
                    raise HttpError(400, "User is already a manager")
                if Manager.objects.filter(
                        user_id=payload.user_id, store=store
                ).exists():
                    cache.set(cache_key_check_manager, Manager.objects.get(user_id=payload.user_id, store=store))
                    raise HttpError(400, "User is already a manager")

                cache_key_check_owner = f"owner_{store.id}_{payload.user_id}"
                check_owner = cache.get(cache_key_check_owner)
                if check_owner is not None:
                    raise HttpError(400, "User is already an owner")
                if Owner.objects.filter(
                        user_id=payload.user_id, store=store
                ).exists():
                    cache.set(cache_key_check_owner, Owner.objects.get(user_id=payload.user_id, store=store))
                    raise HttpError(400, "User is already an owner")

                manager = Manager.objects.create(
                    user_id=payload.user_id, assigned_by=assigning_owner, store=store
                )
        uc.send_notification(
            store.name,
            payload.user_id,
            f"You have been assigned as a manager of {store.name}",
        )
        return {"message": "Manager assigned successfully"}

    def remove_manager(self, request, payload: RemoveManagerSchemaIn):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{payload.store_id}", Store, pk=payload.store_id)
                managing_lock_id = f"{store.pk}_managing_lock"
                cursor.execute(
                    f"SELECT pg_advisory_xact_lock({hash(managing_lock_id)});"
                )
                removing_owner = get_or_set_cache(f"owner_{store.id}_{payload.removed_by}", Owner,
                                                  user_id=payload.removed_by, store=store)
                removed_manager = get_or_set_cache(f"manager_{store.id}_{payload.user_id}", Manager,
                                                   user_id=payload.user_id, store=store)

                if removed_manager.assigned_by != removing_owner:
                    raise HttpError(
                        403,
                        "Manager can only be removed by the owner who assigned them",
                    )

                removed_manager.delete()
                uc.send_notification(
                    store.name,
                    payload.user_id,
                    f"You have been removed as a manager of {store.name}",
                )
                return {"message": "Manager removed successfully"}

    def assign_manager_permissions(
            self,
            request,
            payload: ManagerPermissionSchemaIn,
            manager: RoleSchemaIn,
            assigning_owner_id: int,
    ):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{manager.store_id}", Store, pk=manager.store_id)
                managing_lock_id = f"{store.pk}_managing_lock"
                cursor.execute(
                    f"SELECT pg_advisory_xact_lock({hash(managing_lock_id)});"
                )
                manager = get_or_set_cache(f"manager_{store.id}_{manager.user_id}", Manager, user_id=manager.user_id,
                                           store=store)
                if assigning_owner_id != manager.assigned_by.user_id:
                    raise HttpError(403, "Only assigning owner can assign permissions")
                try:
                    existing_permission, _ = ManagerPermission.objects.update_or_create(
                        manager=manager, defaults=payload.dict()
                    )
                except Exception as e:
                    raise HttpError(500, f"Error assigning permissions: {str(e)}")

        uc.send_notification(
            store.name,
            manager.user_id,
            f"Your permissions have been updated in {store.name}",
        )
        return {"message": "Manager permissions assigned successfully"}

    def get_manager_permissions(self, request, role: RoleSchemaIn, manager_id: int):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{role.store_id}", Store, pk=role.store_id)
                managing_lock_id = f"{store.pk}_managing_lock"
                cursor.execute(
                    f"SELECT pg_advisory_xact_lock({hash(managing_lock_id)});"
                )
                manager = get_or_set_cache(f"manager_{store.id}_{manager_id}", Manager, user_id=manager_id, store=store)
                permissions = get_or_set_cache(f"manager_permissions_{store.id}_{manager.id}", ManagerPermission,
                                               manager=manager)
        return permissions

    def close_store(self, request, payload: RoleSchemaIn):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock(%s);", [store_lock])
                store = get_or_set_cache(f"store_{payload.store_id}", Store, pk=payload.store_id)
                managing_lock_id = f"{store.pk}_managing_lock"
                cursor.execute(
                    f"SELECT pg_advisory_xact_lock_shared({hash(managing_lock_id)});"
                )
                owner = get_or_set_cache(f"owner_{store.id}_{payload.user_id}", Owner, user_id=payload.user_id,
                                         store=store)
                if not owner.is_founder:
                    raise HttpError(403, "Only the founder can close the store")

                store.is_active = False
                store.save()
                store_owners = self.get_owners(request, payload)
                for owner in store_owners:
                    uc.send_notification(
                        store.name, owner.user_id, f"{store.name} has been closed"
                    )

        return {"message": "Store closed successfully"}

    def reopen_store(self, request, payload: RoleSchemaIn):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock(%s);", [store_lock])
                store = get_or_set_cache(f"store_{payload.store_id}", Store, pk=payload.store_id)
                managing_lock_id = f"{store.pk}_managing_lock"
                cursor.execute(
                    f"SELECT pg_advisory_xact_lock_shared({hash(managing_lock_id)});"
                )
                owner = get_or_set_cache(f"owner_{store.id}_{payload.user_id}", Owner, user_id=payload.user_id,
                                         store=store)
                if not owner.is_founder:
                    raise HttpError(403, "Only the founder can reopen the store")

                store.is_active = True
                store.save()
                store_owners = self.get_owners(request, payload)
                for owner in store_owners:
                    uc.send_notification(
                        store.name, owner.user_id, f"{store.name} has been reopened"
                    )

        return {"message": "Store reopened successfully"}

    def get_owners(self, request, payload: RoleSchemaIn):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{payload.store_id}", Store, pk=payload.store_id)
                managing_lock_id = f"{store.pk}_managing_lock"
                cursor.execute(
                    f"SELECT pg_advisory_xact_lock_shared({hash(managing_lock_id)});"
                )

                owner = get_or_set_cache(f"owner_{store.id}_{payload.user_id}", Owner, user_id=payload.user_id,
                                         store=store)
                # reduendent because cache will just return 404 if doenst exist such owner
                #                 if not (
                #                     Owner.objects.filter(user_id=payload.user_id, store=store).exists()
                #                     or Manager.objects.filter(
                #                         user_id=payload.user_id, store=store
                #                     ).exists()
                #                 ):

                owners = Owner.objects.filter(store=store)
                cache.set_many({f"owner_{store.id}_{owner.user_id}": owner for owner in owners})

        return owners

    def get_managers(self, request, payload: RoleSchemaIn):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{payload.store_id}", Store, pk=payload.store_id)
                managing_lock_id = f"{store.pk}_managing_lock"
                cursor.execute(
                    f"SELECT pg_advisory_xact_lock_shared({hash(managing_lock_id)});"
                )

                owner = get_or_set_cache(f"owner_{store.id}_{payload.user_id}", Owner, user_id=payload.user_id,
                                         store=store)
                #                 if not (
                #                     Owner.objects.filter(user_id=payload.user_id, store=store).exists()
                #                     or Manager.objects.filter(
                #                         user_id=payload.user_id, store=store
                #                     ).exists()
                #                 ):
                managers = Manager.objects.filter(store=store)
                cache.set_many({f"manager_{store.id}_{manager.user_id}": manager for manager in managers})

        return managers

    def add_purchase_policy(
            self,
            request,
            role: RoleSchemaIn,
            payload: Union[
                SimplePurchasePolicySchemaIn,
                ConditionalPurchasePolicySchemaIn,
                CompositePurchasePolicySchemaIn,
            ],
    ):
        if request is not None and role is not None:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT pg_advisory_xact_lock_shared(%s);", [store_lock]
                    )
                    store = get_or_set_cache(f"store_{payload.store_id}", Store, pk=payload.store_id)
                    self.validate_permissions(
                        role, store, "can_add_purchase_policy", cursor
                    )
        if isinstance(payload, SimplePurchasePolicySchemaIn):
            return self.add_simple_purchase_policy(payload)
        elif isinstance(payload, ConditionalPurchasePolicySchemaIn):
            return self.add_conditional_purchase_policy(payload)
        elif isinstance(payload, CompositePurchasePolicySchemaIn):
            return self.add_composite_purchase_policy(payload)

    def add_simple_purchase_policy(self, payload: SimplePurchasePolicySchemaIn):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{payload.store_id}", Store, pk=payload.store_id)
                policy_lock = f"{store.pk}_policy_lock"
                cursor.execute(f"SELECT pg_advisory_xact_lock({hash(policy_lock)});")
                policy = SimplePurchasePolicy.objects.create(
                    store=store,
                    is_root=payload.is_root,
                )
                condition = Condition.objects.create(
                    applies_to=payload.condition.applies_to,
                    name_of_apply=payload.condition.name_of_apply,
                    condition=payload.condition.condition,
                    value=payload.condition.value,
                    purchase_policy=policy,
                )
        return {
            "message": "Simple purchase policy added successfully",
            "policy": policy,
        }

    def add_conditional_purchase_policy(
            self, payload: ConditionalPurchasePolicySchemaIn
    ):
        restriction = self.add_purchase_policy(None, None, payload.restriction).get(
            "policy"
        )
        condition = self.add_purchase_policy(None, None, payload.condition).get(
            "policy"
        )

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{payload.store_id}", Store, pk=payload.store_id)
                policy_lock = f"{store.pk}_policy_lock"
                cursor.execute(f"SELECT pg_advisory_xact_lock({hash(policy_lock)});")
                policy = ConditionalPurchasePolicy.objects.create(
                    store=store,
                    is_root=payload.is_root,
                    restriction=restriction,
                    condition=condition,
                )
        return {
            "message": "Conditional purchase policy added successfully",
            "policy": policy,
        }

    def add_composite_purchase_policy(self, payload: CompositePurchasePolicySchemaIn):

        policies = []
        for policy_payload in payload.policies:
            policies.append(
                self.add_purchase_policy(None, None, policy_payload).get("policy")
            )

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{payload.store_id}", Store, pk=payload.store_id)
                policy_lock = f"{store.pk}_policy_lock"
                cursor.execute(f"SELECT pg_advisory_xact_lock({hash(policy_lock)});")
                policy = CompositePurchasePolicy.objects.create(
                    store=store,
                    is_root=payload.is_root,
                    combine_function=payload.combine_function,
                )
                policy.policies.set(policies)
        return {
            "message": "Composite purchase policy added successfully",
            "policy": policy,
        }

    def remove_purchase_policy(
            self, request, role: RoleSchemaIn, payload: RemovePurchasePolicySchemaIn
    ):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{payload.store_id}", Store, pk=payload.store_id)
                self.validate_permissions(
                    role, store, "can_remove_purchase_policy", cursor
                )
                policy_lock = f"{store.pk}_policy_lock"
                cursor.execute(f"SELECT pg_advisory_xact_lock({hash(policy_lock)});")
                policy = get_or_set_cache(f"purchase_policy_{store.id}_{payload.policy_id}", PurchasePolicyBase,
                                          pk=payload.policy_id, store=store, is_root=True)
                policy.delete()
        return {"message": "Purchase policy removed successfully"}

    def get_purchase_policies(self, request, role: RoleSchemaIn):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{role.store_id}", Store, pk=role.store_id)
                if not store.is_active:
                    managing_lock_id = hash(f"{store.pk}_managing_lock")
                    cursor.execute(
                        "SELECT pg_advisory_xact_lock_shared(%s);", [managing_lock_id]
                    )
                    owner = get_or_set_cache(f"owner_{store.id}_{role.user_id}", Owner, user_id=role.user_id,
                                             store=store)
                    # if not Owner.objects.filter(
                    #         user_id=role.user_id, store=store
                    # ).exists():
                    #     raise HttpError(
                    #         403,
                    #         "User is not an owner of the store and the store is closed",
                    #     )
                policy_lock = f"{store.pk}_policy_lock"
                cursor.execute(
                    f"SELECT pg_advisory_xact_lock_shared({hash(policy_lock)});"
                )
                policies = PurchasePolicyBase.objects.filter(store=store, is_root=True)
                cache.set_many({f"purchase_policy_{store.id}_{policy.id}": policy for policy in policies})
        return policies

    def add_discount_policy(
            self,
            request,
            role: RoleSchemaIn,
            payload: Union[
                SimpleDiscountSchemaIn,
                ConditionalDiscountSchemaIn,
                CompositeDiscountSchemaIn,
            ],
    ):

        # Check if the user is authorized to add a discount policy
        if request is not None and role is not None:  # none only in recursive calls
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT pg_advisory_xact_lock_shared(%s);", [store_lock]
                    )
                    store = get_or_set_cache(f"store_{payload.store_id}", Store, pk=payload.store_id)
                    self.validate_permissions(
                        role, store, "can_add_discount_policy", cursor
                    )

        if isinstance(payload, SimpleDiscountSchemaIn):
            return self.add_simple_discount_policy(payload)
        elif isinstance(payload, CompositeDiscountSchemaIn):
            return self.add_composite_discount_policy(payload)
        elif isinstance(payload, ConditionalDiscountSchemaIn):
            return self.add_conditional_discount_policy(payload)

    def add_simple_discount_policy(self, payload: SimpleDiscountSchemaIn):
        if payload.percentage <= 0 or payload.percentage > 100:
            raise HttpError(400, "Discount percentage must be between 1 and 100")
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{payload.store_id}", Store, pk=payload.store_id)
                discount_lock = f"{store.pk}_discount_lock"
                cursor.execute(f"SELECT pg_advisory_xact_lock({hash(discount_lock)});")
                discount = SimpleDiscount.objects.create(
                    store=store,
                    is_root=payload.is_root,
                    percentage=payload.percentage,
                    applicable_categories=json.dumps(payload.applicable_categories),
                )
                if payload.applicable_products:
                    products_lock = f"{store.pk}_products_lock"
                    cursor.execute(
                        f"SELECT pg_advisory_xact_lock_shared({hash(products_lock)});"
                    )
                    for product in payload.applicable_products:
                        product_instance = get_or_set_cache(f"product_{store.id}_{product}", StoreProduct, store=store,
                                                            name=product)
                        discount.applicable_products.add(product_instance)

        return {
            "message": "Simple discount policy added successfully",
            "discount": discount,
        }

    def add_conditional_discount_policy(self, payload: ConditionalDiscountSchemaIn):

        base_discount = (self.add_discount_policy(None, None, payload.discount)).get(
            "discount"
        )
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{payload.store_id}", Store, pk=payload.store_id)
                discount_lock = f"{store.pk}_discount_lock"
                cursor.execute(f"SELECT pg_advisory_xact_lock({hash(discount_lock)});")
                discount = ConditionalDiscount.objects.create(
                    is_root=payload.is_root, store=store, discount=base_discount
                )

                condition = Condition.objects.create(
                    applies_to=payload.condition.applies_to,
                    name_of_apply=payload.condition.name_of_apply,
                    condition=payload.condition.condition,
                    value=payload.condition.value,
                    discount=discount,
                )

        return {
            "message": "Conditional discount policy added successfully",
            "discount": discount,
        }

    def add_composite_discount_policy(self, payload: CompositeDiscountSchemaIn):
        discounts = []
        for discount_payload in payload.discounts:
            discounts.append(
                (self.add_discount_policy(None, None, discount_payload)).get("discount")
            )

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{payload.store_id}", Store, pk=payload.store_id)
                discount_lock = f"{store.pk}_discount_lock"
                cursor.execute(f"SELECT pg_advisory_xact_lock({hash(discount_lock)});")
                discount = CompositeDiscount.objects.create(
                    is_root=payload.is_root,
                    store=store,
                    combine_function=payload.combine_function,
                )
                discount.discounts.set(discounts)

                for conditions in payload.conditions:
                    condition = Condition.objects.create(
                        applies_to=conditions.applies_to,
                        name_of_apply=conditions.name_of_apply,
                        condition=conditions.condition,
                        value=conditions.value,
                        discount=discount,
                    )
        return {
            "message": "Composite discount policy added successfully",
            "discount": discount,
        }

    def remove_discount_policy(
            self, request, role: RoleSchemaIn, payload: RemoveDiscountSchemaIn
    ):

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{payload.store_id}", Store, pk=payload.store_id)
                self.validate_permissions(
                    role, store, "can_remove_discount_policy", cursor
                )
                discount_lock = f"{store.pk}_discount_lock"
                cursor.execute(f"SELECT pg_advisory_xact_lock({hash(discount_lock)});")
                discount_instance = get_or_set_cache(f"discount_{store.id}_{payload.discount_id}", DiscountBase,
                                                     pk=payload.discount_id, store=store, is_root=True)
                discount_instance.delete()

        return {"message": "Discount policy removed successfully"}

    def get_discount_policies(self, request, role: RoleSchemaIn):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{role.store_id}", Store, pk=role.store_id)
                if not store.is_active:
                    managing_lock_id = hash(f"{store.pk}_managing_lock")
                    cursor.execute(
                        "SELECT pg_advisory_xact_lock_shared(%s);", [managing_lock_id]
                    )
                    owner = get_or_set_cache(f"owner_{store.id}_{role.user_id}", Owner, user_id=role.user_id,
                                             store=store)
                    # if not Owner.objects.filter(
                    #         user_id=role.user_id, store=store
                    # ).exists():
                    #     raise HttpError(
                    #         403,
                    #         "User is not an owner of the store and the store is closed",
                    #     )
                discount_lock = f"{store.pk}_discount_lock"
                cursor.execute(
                    f"SELECT pg_advisory_xact_lock_shared({hash(discount_lock)});"
                )
                discounts = DiscountBase.objects.filter(store=store, is_root=True)
                cache.set_many({f"discount_{store.id}_{discount.id}": discount for discount in discounts})

        return discounts

    def get_conditions(self, request, payload: GetConditionsSchemaIn):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{payload.store_id}", Store, pk=payload.store_id)
                if payload.to_discount:
                    discount_lock = f"{store.pk}_discount_lock"
                    cursor.execute(
                        f"SELECT pg_advisory_xact_lock_shared({hash(discount_lock)});"
                    )
                    discount = get_or_set_cache(f"discount_{store.id}_{payload.target_id}", DiscountBase,
                                                pk=payload.target_id)
                    conditions = discount.conditions.all()
                    #conditions not saved in cache
                else:
                    policy_lock = f"{store.pk}_policy_lock"
                    cursor.execute(
                        f"SELECT pg_advisory_xact_lock_shared({hash(policy_lock)});"
                    )
                    # first check if composite
                    try:
                        policy = get_or_set_cache(f"purchase_policy_{store.id}_{payload.target_id}",
                                                  CompositePurchasePolicy, pk=payload.target_id)
                        policies = policy.policies.all()
                        conditions = [
                            condition
                            for policy in policies
                            for condition in policy.conditions.all()
                        ]
                    except Http404:
                        policy = get_or_set_cache(f"purchase_policy_{store.id}_{payload.target_id}", PurchasePolicyBase,
                                                  pk=payload.target_id)
                        conditions = policy.conditions.all()
        return conditions

    def get_combine_function_for_policy(self, request, payload: GetConditionsSchemaIn):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{payload.store_id}", Store, pk=payload.store_id)
                if not payload.to_discount:
                    policy_lock = f"{store.pk}_policy_lock"
                    cursor.execute(
                        f"SELECT pg_advisory_xact_lock_shared({hash(policy_lock)});"
                    )
                    try:
                        policy = get_or_set_cache(f"purchase_policy_{store.id}_{payload.target_id}",
                                                  CompositePurchasePolicy, pk=payload.target_id)
                        return policy.combine_function
                    except Http404:
                        return None

    def validate_permissions(
            self, role: RoleSchemaIn, store: Store, permission: str, cursor
    ):
        managing_lock = hash(f"{store.pk}_managing_lock")
        cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [managing_lock])
        try:
            owner = get_or_set_cache(f"owner_{store.id}_{role.user_id}", Owner, user_id=role.user_id, store=store)
        except Http404:
            try:
                manager = get_or_set_cache(f"manager_{store.id}_{role.user_id}", Manager, user_id=role.user_id,
                                           store=store)
            except Http404:
                raise HttpError(403, "User is not an owner or manager of the store")

            manager_permissions = get_or_set_cache(f"manager_permissions_{store.id}_{manager.id}", ManagerPermission,
                                                   manager=manager)
            if not getattr(manager_permissions, permission):
                raise HttpError(
                    403,
                    f"Manager does not have permission to {permission.replace('_', ' ')}",
                )

    def add_product(self, request, role: RoleSchemaIn, payload: StoreProductSchemaIn):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{role.store_id}", Store, pk=role.store_id)
                self.validate_permissions(role, store, "can_add_product", cursor)
                products_lock = f"{store.pk}_products_lock"
                cursor.execute(f"SELECT pg_advisory_xact_lock({hash(products_lock)});")
                if payload.quantity <= 0:
                    raise HttpError(400, "Product quantity cannot be 0 or negative")
                if payload.initial_price <= 0:
                    raise HttpError(400, "Product price cannot be 0 or negative")
                try:
                    product = get_or_set_cache(f"store_product_{store.id}_{payload.name}", StoreProduct, store=store,
                                               name=payload.name)  #if we get 404 thats good because it means product doesnt
                    #exist
                    raise HttpError(400, "Product with this name already exists in the store")
                except Http404:
                    product = StoreProduct.objects.create(store=store, **payload.dict())

        return {"message": "Product added successfully"}

    def remove_product(self, request, role: RoleSchemaIn, product_name: str):

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{role.store_id}", Store, pk=role.store_id)
                self.validate_permissions(role, store, "can_delete_product", cursor)
                products_lock = f"{store.pk}_products_lock"
                cursor.execute(f"SELECT pg_advisory_xact_lock({hash(products_lock)});")
                product = get_or_set_cache(f"store_product_{store.id}_{product_name}", StoreProduct, store=store,
                                           name=product_name)
                product.delete()

        return {"message": "Product removed successfully"}

    def edit_product(self, request, role: RoleSchemaIn, payload: StoreProductSchemaIn):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{role.store_id}", Store, pk=role.store_id)
                self.validate_permissions(role, store, "can_edit_product", cursor)
                products_lock = f"{store.pk}_products_lock"
                cursor.execute(f"SELECT pg_advisory_xact_lock({hash(products_lock)});")
                product = get_or_set_cache(f"store_product_{store.id}_{payload.name}", StoreProduct, store=store,
                                           name=payload.name)
                if payload.quantity <= 0:
                    raise HttpError(
                        400,
                        "Product quantity cannot be negative. To remove the product, delete it instead.",
                    )
                if payload.initial_price <= 0:
                    raise HttpError(400, "Product price cannot be negative.")

                # Update the product attributes
                product.quantity = payload.quantity
                product.initial_price = payload.initial_price
                product.category = payload.category
                product.image_link = payload.image_link
                product.save()

        return {"message": "Product edited successfully"}

    def get_products(self, request, store_id: int, role: RoleSchemaIn):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{store_id}", Store, pk=store_id)
                if not store.is_active:
                    managing_lock = hash(f"{store.pk}_managing_lock")
                    cursor.execute(
                        "SELECT pg_advisory_xact_lock_shared(%s);", [managing_lock]
                    )
                    owner = get_or_set_cache(f"owner_{store.id}_{role.user_id}", Owner, user_id=role.user_id,
                                             store=store)
                    # if not Owner.objects.filter(
                    #         user_id=role.user_id, store=store
                    # ).exists():
                    #     raise HttpError(
                    #         403,
                    #         "User is not an owner of the store and the store is closed",
                    #     )
                products_lock = f"{store.pk}_products_lock"
                cursor.execute(
                    f"SELECT pg_advisory_xact_lock_shared({hash(products_lock)});"
                )
                products = StoreProduct.objects.filter(store=store)
                cache.set_many({f"store_product_{store.id}_{product.name}": product for product in products})

        return products

    def get_product_clean(self, request, store_id: int):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{store_id}", Store, pk=store_id)
                products_lock = f"{store.pk}_products_lock"
                cursor.execute(
                    f"SELECT pg_advisory_xact_lock_shared({hash(products_lock)});"
                )
                products = StoreProduct.objects.filter(store=store)
                cache.set_many({f"store_product_{store.id}_{product.name}": product for product in products})

        return products

    def purchase_product(
            self, request, store_id: int, payload: List[PurchaseStoreProductSchema]
    ):
        if payload is None or len(payload) == 0:
            raise HttpError(400, "No products to purchase")

        with transaction.atomic():
            with connection.cursor() as cursor:
                # Acquire an advisory lock on the store
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{store_id}", Store, pk=store_id)
                total_items = sum(item.quantity for item in payload)
                products_lock = f"{store.pk}_products_lock"
                cursor.execute(f"SELECT pg_advisory_xact_lock({hash(products_lock)});")
                products = [
                    get_or_set_cache(f"store_product_{store.id}_{item.product_name}", StoreProduct, store=store,
                                     name=item.product_name)
                    for item in payload
                ]
                total_price = sum(
                    [
                        product.initial_price * item.quantity
                        for product, item in zip(products, payload)
                    ]
                )
                original_total_price = total_price

                original_prices = [
                    {
                        "name": product.name,
                        "initial price": product.initial_price,
                        "quantity": item.quantity,
                        "total price": product.initial_price * item.quantity,
                    }
                    for product, item in zip(products, payload)
                ]

                self.validate_purchase_policy(
                    payload=payload, cursor=cursor, store=store
                )

                total_price -= self.calculate_cart_discount(payload, store=store, cursor=cursor)
                for product, item in zip(products, payload):
                    if product.quantity < item.quantity:
                        raise HttpError(
                            400, f"Insufficient quantity of {product.name} in store"
                        )
                    product.quantity -= item.quantity
                    if product.quantity == 0:
                        product.delete()
                    else:
                        product.save()

                managing_lock = hash(f"{store.pk}_managing_lock")
                cursor.execute(
                    "SELECT pg_advisory_xact_lock_shared(%s);", [managing_lock]
                )
                owners = Owner.objects.filter(store=store)
                cache.set_many({f"owner_{store.id}_{owner.user_id}": owner for owner in owners})
                for owner in owners:
                    uc.send_notification(
                        store.name,
                        owner.user_id,
                        f"{total_items} products have been purchased from {store.name}",
                    )

        return {
            "message": "Products purchased successfully",
            "total_price": total_price,
            "original_price": original_total_price,
            "original_prices": original_prices,
        }

    def return_products(
            self, request, store_id: int, payload: List[PurchaseStoreProductSchema]
    ):
        if payload is None or len(payload) == 0:
            raise HttpError(400, "No products to return")

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{store_id}", Store, pk=store_id)
                products_lock = f"{store.pk}_products_lock"
                cursor.execute(f"SELECT pg_advisory_xact_lock({hash(products_lock)});")
                for item in payload:
                    product = get_or_set_cache(f"store_product_{store.id}_{item.product_name}", StoreProduct,
                                               store=store, name=item.product_name)
                    product.quantity += item.quantity
                    product.save()

        return {"message": "Products returned successfully"}

    def get_discount_instance(self, discount_model: DiscountBase, store: Store):
        if isinstance(discount_model, SimpleDiscount):
            return SimpleDiscountClass(
                percentage=discount_model.percentage,
                applicable_products=discount_model.applicable_products.all(),
                applicable_categories=get_list_from_string(
                    discount_model.applicable_categories
                ),
                store=store,
            )
        elif isinstance(discount_model, ConditionalDiscount):
            condition_name = discount_model.conditions.all()
            related_discount = self.get_discount_instance(
                discount_model.discount, store
            )
            return ConditionalDiscountClass(condition_name, related_discount, store)
        elif isinstance(discount_model, CompositeDiscount):
            discounts = [
                self.get_discount_instance(d, store)
                for d in discount_model.discounts.all()
            ]
            conditions = discount_model.conditions.all()
            return CompositeDiscountClass(
                discounts, discount_model.combine_function, conditions, store
            )
        return None

    def calculate_cart_discount(
            self,
            purchase_products: List[PurchaseStoreProductSchema],
            store_id: int = None,
            store: Store = None,
            cursor=None,
    ):
        total_discount = 0
        # Retrieve only root discount models to avoid duplicates
        if (
                cursor is not None and store is not None
        ):  # after we have the cursor on the db and the store itself
            discount_lock = f"{store.pk}_discount_lock"
            cursor.execute(
                f"SELECT pg_advisory_xact_lock_shared({hash(discount_lock)});"
            )
            all_discount_models = DiscountBase.objects.filter(is_root=True)
            cache.set_many({f"discount_{store.id}_{discount.id}": discount for discount in all_discount_models})
            for discount_model in all_discount_models:
                discount_instance = self.get_discount_instance(discount_model, store)
                if discount_instance:
                    discount = discount_instance.apply_discount(purchase_products)
                    if discount:
                        total_discount += discount
        else:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(f"SELECT pg_advisory_xact_lock_shared({store_lock});")
                    store = get_or_set_cache(f"store_{store_id}", Store, pk=store_id)
                    return self.calculate_cart_discount(purchase_products, store=store, cursor=cursor)

        return total_discount

    def get_purchase_policy_instance(
            self, purchase_model: PurchasePolicyBase, store: Store
    ):
        if isinstance(purchase_model, SimplePurchasePolicy):
            return SimplePurchasePolicyClass(
                condition=purchase_model.conditions.all(), store=store
            )
        elif isinstance(purchase_model, ConditionalPurchasePolicy):
            condition = self.get_purchase_policy_instance(
                purchase_model.condition, store
            )
            restriction = self.get_purchase_policy_instance(
                purchase_model.restriction, store
            )
            return ConditionalPurchasePolicyClass(
                condition=condition, restriction=restriction, store=store
            )
        elif isinstance(purchase_model, CompositePurchasePolicy):
            policies = [
                self.get_purchase_policy_instance(p, store)
                for p in purchase_model.policies.all()
            ]
            return CompositePurchasePolicyClass(
                policies=policies,
                combine_function=purchase_model.combine_function,
                store=store,
            )
        return None

    def validate_purchase_policy(
            self,
            payload: List[PurchaseStoreProductSchema],
            store_id: int = None,
            cursor=None,
            store: Store = None,
    ):  # Retrieve only root purchase models to avoid duplicates
        if cursor is not None and store is not None:
            policy_lock = f"{store.pk}_policy_lock"
            cursor.execute(f"SELECT pg_advisory_xact_lock_shared({hash(policy_lock)});")
            all_purchase_models = PurchasePolicyBase.objects.filter(is_root=True)
            cache.set_many({f"purchase_policy_{store.id}_{policy.id}": policy for policy in all_purchase_models})
            if len(all_purchase_models) == 0:
                return True
            result = reduce(
                operator.and_,
                [
                    self.get_purchase_policy_instance(policy, store).apply_policy(
                        payload
                    )
                    for policy in all_purchase_models
                ],
            )  # all purchase policies should work
            if not result:
                raise HttpError(400, "Purchase policy validation failed")
        else:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                    store = get_or_set_cache(f"store_{store_id}", Store, pk=store_id)
                    return self.validate_purchase_policy(payload=payload, cursor=cursor, store=store)

    #search is not used so i dont update cache
    def search_products(
            self, request, search_query: SearchSchema, filter_query: FilterSearchSchema
    ):
        with transaction.atomic():
            with connection.cursor() as cursor:
                products_lock = f"{search_query.store_id}_products_lock"
                cursor.execute(
                    f"SELECT pg_advisory_xact_lock_shared({hash(products_lock)});"
                )
                if search_query.store_id:
                    cursor.execute(
                        "SELECT pg_advisory_xact_lock_shared(%s);", [store_lock]
                    )
                    store = get_or_set_cache(f"store_{search_query.store_id}", Store, pk=search_query.store_id)
                    if not store.is_active:
                        raise HttpError(403, "Store is closed")
                    if search_query.product_name and not search_query.category:
                        products = StoreProduct.objects.filter(
                            store=store, name__icontains=search_query.product_name
                        )
                    elif search_query.category and not search_query.product_name:
                        products = StoreProduct.objects.filter(
                            store=store, category__icontains=search_query.category
                        )
                    elif search_query.product_name and search_query.category:
                        products = StoreProduct.objects.filter(
                            store=store,
                            name__icontains=search_query.product_name,
                            category__icontains=search_query.category,
                        )
                    else:
                        products = StoreProduct.objects.filter(store=store)
                else:
                    if search_query.product_name and not search_query.category:
                        products = StoreProduct.objects.filter(
                            name__icontains=search_query.product_name,
                            store__is_active=True,
                        )
                    elif search_query.category and not search_query.product_name:
                        products = StoreProduct.objects.filter(
                            category__icontains=search_query.category,
                            store__is_ative=True,
                        )
                    elif search_query.product_name and search_query.category:
                        products = StoreProduct.objects.filter(
                            name__icontains=search_query.product_name,
                            category__icontains=search_query.category,
                            store__is_active=True,
                        )
                    else:
                        products = StoreProduct.objects.filter(store__is_active=True)

                if filter_query.min_price:
                    products = products.filter(
                        initial_price__gte=filter_query.min_price
                    )
                if filter_query.max_price:
                    products = products.filter(
                        initial_price__lte=filter_query.max_price
                    )
                if filter_query.min_quantity:
                    products = products.filter(quantity__gte=filter_query.min_quantity)
                if filter_query.max_quantity:
                    products = products.filter(quantity__lte=filter_query.max_quantity)

        return products

    def create_fake_data(self):
        store_data = {
            "Hummus Heaven": {
                "category": "Food",
                "products": ["Classic Hummus", "Spicy Hummus", "Garlic Hummus"],
                "Links": [
                    "https://www.eatingwell.com/thmb/whG5O2XFksPLrc73YGNoRiYNrFQ=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/6080917-adf6cf9f2c1944a9bfbaeadd032013a5.jpg",
                    "https://heartbeetkitchen.com/foodblog/wp-content/uploads/2023/03/spicy-hummus-13.jpg",
                    "https://shoppy.co.il/cdn/shop/products/ahlahummuslemongarlic_720x.png?v=1641413539",
                ],
            },
            "Falafel Fiesta": {
                "category": "Food",
                "products": ["Falafel Wrap", "Falafel Plate", "Falafel Salad"],
                "Links": [
                    "https://cookingwithayeh.com/wp-content/uploads/2024/03/Falafel-Wrap-1.jpg",
                    "https://hilahcooking.com/wp-content/uploads/2017/03/spicy-falafel.jpg",
                    "https://kitchenconfidante.com/wp-content/uploads/2019/05/Falafel-Salad-kitchenconfidante.com-9021.jpg",
                ],
            },
            "Startup Nation Tech": {
                "category": "Technology",
                "products": [
                    "Israeli Smartphone",
                    "Kibbutz Laptop",
                    "Jerusalem Smartwatch",
                ],
                "Links": [
                    "https://static.timesofisrael.com/www/uploads/2022/07/F210127YS44-640x400.jpg",
                    "https://cdn.thewirecutter.com/wp-content/media/2023/06/bestlaptops-2048px-9765.jpg?auto=webp&quality=75&width=1024&dpr=2",
                    "https://m.media-amazon.com/images/I/61ksrJ2LsgL._AC_SX679_.jpg",
                ],
            },
            "Tel Aviv Trends": {
                "category": "Clothing",
                "products": [
                    "Sabra Designer Dress",
                    "Negev Leather Jacket",
                    "Eilat Running Shoes",
                ],
                "Links": [
                    "https://i.ebayimg.com/images/g/JlEAAOSwKmphgYSh/s-l1600.jpg",
                    "https://img01.ztat.net/article/spp-media-p1/13e0e8a354eb4656a895b06a3e324f9b/305d7df6e4f34e339a1cf31b585adbd4.jpg?imwidth=762",
                    "https://contents.mediadecathlon.com/p2606890/k$30ab17a373351d4761e138a9c3be9b02/jogflow-5001-men-s-running-shoes-white-blue-red.jpg?format=auto&quality=40&f=452x452",
                ],
            },
            "Book Bazaar Israel": {
                "category": "Books",
                "products": [
                    "Hebrew Science Fiction Novel",
                    "Israeli Cookbook",
                    "Zionist Historical Biography",
                ],
                "Links": [
                    "https://mosaicmagazine.com/wp-content/uploads/2018/10/Weingrad-ZF.jpg",
                    "https://m.media-amazon.com/images/I/81KRghJo4YL._SL1500_.jpg",
                    "https://www.urimpublications.com/mm5/graphics/00000001/historyzionismWeb2.jpg",
                ],
            },
            "Toy Town Israel": {
                "category": "Toys",
                "products": [
                    "David Ben-Gurion Action Figure",
                    "Israeli Board Game",
                    "Jerusalem Puzzle Set",
                ],
                "Links": [
                    "https://asufadesign.com/cdn/shop/files/BG-Product-PNG.png?v=1707639053",
                    "https://www.dvarimbego.co.il/pub/123432/%D7%9E%D7%A9%D7%97%D7%A7%D7%99%20%D7%A9%D7%A4%D7%99%D7%A8/3694571.jpg?quality=65&height=380&mode=max",
                    "https://eurographics.blob.core.windows.net/45a2776f-ae2f-4bb8-9e22-db4ab5a98cbe/ProductManagement/Products/01dd2e93-d552-4a74-b7cf-ae9fe130c1fa/6010-5550.jpg?t=638539811317412640",
                ],
            },
        }

        stores = []
        store_names = list(store_data.keys())
        for i in range(len(store_names)):
            stores.append(
                Store.objects.create(
                    name=store_names[i],
                    description=f"This is {store_names[i]} {i}",
                    is_active=True,
                )
            )

        for i in range(len(stores)):
            owner = Owner.objects.create(user_id=i, store=stores[i], is_founder=True)
            manager = Manager.objects.create(
                user_id=2 * len(store_names) - i - 1, store=stores[i], assigned_by=owner
            )
            manager_permissions = ManagerPermission.objects.create(
                manager=manager,
                can_add_product=True,
                can_delete_product=True,
                can_edit_product=True,
                can_add_discount_policy=True,
                can_remove_discount_policy=True,
                can_add_purchase_policy=True,
                can_remove_purchase_policy=True,
            )
            for j in range(3):
                product = StoreProduct.objects.create(
                    store=stores[i],
                    name=store_data[store_names[i]]["products"][j],
                    category=store_data[store_names[i]]["category"],
                    quantity=10,
                    initial_price=random.randint(10, 100),
                    image_link=store_data[store_names[i]]["Links"][j],
                )

                # Create a simple discount
                simple_discount = SimpleDiscount.objects.create(
                    store=stores[i],
                    is_root=True,
                    percentage=10,
                    applicable_categories=json.dumps(
                        [store_data[store_names[i]]["category"]]
                    ),
                )
                simple_discount.applicable_products.set([product])
                simple_discount.save()

                # Create a conditional discount
                payload_dict = {
                    "store_id": stores[i].id,
                    "is_root": True,
                    "condition": {
                        "applies_to": "product",
                        "name_of_apply": store_data[store_names[i]]["products"][j],
                        "condition": "at_least",
                        "value": 5,
                    },
                    "discount": {
                        "store_id": stores[i].id,
                        "is_root": False,
                        "percentage": 15.0,
                        "applicable_categories": [
                            store_data[store_names[i]]["category"]
                        ],
                        "applicable_products": [
                            str(product.name)
                        ],  # Use the product ID as a string
                    },
                }

                condition_schema = ConditionSchema(**payload_dict["condition"])
                discount_data = payload_dict["discount"]
                discount_data["applicable_categories"] = json.loads(
                    json.dumps(discount_data["applicable_categories"])
                )
                simple_discount_schema = SimpleDiscountSchemaIn(**discount_data)

                payload = ConditionalDiscountSchemaIn(
                    store_id=payload_dict["store_id"],
                    is_root=payload_dict["is_root"],
                    condition=condition_schema,
                    discount=simple_discount_schema,
                )
                self.add_conditional_discount_policy(payload)

                # Create simple purchase policies
                condition1 = {
                    "applies_to": "product",
                    "name_of_apply": product.name,
                    "condition": "at_most",
                    "value": 5,
                }
                purchase_policy_payload1 = {
                    "store_id": stores[i].id,
                    "is_root": True,
                    "condition": condition1,
                }
                simple_policy_schema1 = SimplePurchasePolicySchemaIn(
                    **purchase_policy_payload1
                )
                self.add_simple_purchase_policy(simple_policy_schema1)

                condition2 = {
                    "applies_to": "time",
                    "name_of_apply": "",
                    "condition": "at_most",
                    "value": 23,
                }
                purchase_policy_payload2 = {
                    "store_id": stores[i].id,
                    "is_root": True,
                    "condition": condition2,
                }
                simple_policy_schema2 = SimplePurchasePolicySchemaIn(
                    **purchase_policy_payload2
                )
                self.add_simple_purchase_policy(simple_policy_schema2)
                purchase_policy_payload1["is_root"] = False
                purchase_policy_payload2["is_root"] = False
                # Create a composite purchase policy
                composite_policy_payload = {
                    "store_id": stores[i].id,
                    "is_root": True,
                    "policies": [purchase_policy_payload1, purchase_policy_payload2],
                    "combine_function": "logical_and",
                }
                composite_policy_schema = CompositePurchasePolicySchemaIn(
                    **composite_policy_payload
                )
                self.add_composite_purchase_policy(composite_policy_schema)

        return {"message": "Fake data created successfully"}

    def make_bid(self, request, payload: BidSchemaIn):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{payload.store_id}", Store, pk=payload.store_id)
                products_lock = f"{store.pk}_products_lock"
                cursor.execute(
                    f"SELECT pg_advisory_xact_lock_shared({hash(products_lock)});"
                )
                product = get_or_set_cache(f"store_product_{store.id}_{payload.product_name}", StoreProduct,
                                           store=store, name=payload.product_name)
                bids_lock = f"{store.pk}_bids_lock"
                cursor.execute(f"SELECT pg_advisory_xact_lock({hash(bids_lock)});")
                bid = Bid.objects.create(
                    store=store,
                    product=product,
                    price=payload.price,
                    user_id=payload.user_id,
                    quantity=payload.quantity,
                )
                managing_lock = hash(f"{store.pk}_managing_lock")
                cursor.execute(
                    "SELECT pg_advisory_xact_lock_shared(%s);", [managing_lock]
                )
                owners = Owner.objects.filter(store=store)
                cache.set_many({f"owner_{store.id}_{owner.user_id}": owner for owner in owners})
                managers_with_permission = self.get_managers_with_permissions(
                    store.pk, "can_decide_on_bid"
                )
                for owner in owners:
                    uc.send_notification(
                        store.name,
                        owner.user_id,
                        f"A bid has been made on {product.name} in {store.name}",
                    )
                for manager in managers_with_permission:
                    uc.send_notification(
                        store.name,
                        manager.user_id,
                        f"A bid has been made on {product.name} in {store.name}",
                    )

        return {"message": "Bid added successfully"}

    def decide_on_bid(self, request, role: RoleSchemaIn, payload: DecisionBidSchemaIn):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{role.store_id}", Store, pk=role.store_id)
                bids_lock = f"{store.pk}_bids_lock"
                cursor.execute(f"SELECT pg_advisory_xact_lock({hash(bids_lock)});")
                bid = get_or_set_cache(f"bid_{store.id}_{payload.bid_id}", Bid, pk=payload.bid_id)
                self.validate_permissions(role, bid.store, "can_decide_on_bid", cursor)
                managing_lock = hash(f"{store.pk}_managing_lock")
                cursor.execute(
                    "SELECT pg_advisory_xact_lock_shared(%s);", [managing_lock]
                )
                managers_with_permission = self.get_managers_with_permissions(
                    role.store_id, "can_decide_on_bid"
                )
                try:
                    manager = get_or_set_cache(f"manager_{store.id}_{role.user_id}", Manager, user_id=role.user_id,
                                               store=bid.store)
                except Http404:
                    manager = get_or_set_cache(f"owner_{store.id}_{role.user_id}", Owner, user_id=role.user_id,
                                               store=bid.store)
                if manager in bid.accepted_by.all():
                    raise HttpError(400, "Manager has already accepted the bid")
                # if manager not in managers_with_permission:
                #     raise HttpError(403, "Manager does not have permission to decide on bids")
                if payload.decision:
                    bid.accepted_by.add(manager)
                    owners_count = self.get_owners(None, role).count()
                    count_managers_with_permission = len(managers_with_permission)
                    if (
                            bid.accepted_by.count()
                            == owners_count + count_managers_with_permission
                    ):
                        bid.can_purchase = True
                        bid.save()  # Ensure bid is saved after setting can_purchase to True
                        uc.send_notification(
                            store.name,
                            bid.user_id,
                            f"Your bid on {bid.product.name} in {bid.store.name} has been accepted, you can now purchase the product",
                        )
                else:
                    #bid.delete()
                    uc.send_notification(
                        store.name,
                        bid.user_id,
                        f"Your bid on {bid.product.name} in {bid.store.name} has been rejected",
                    )

        return {"message": "Bid decision made successfully"}

    def get_bids(self, request, role: RoleSchemaIn, store_id: int):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{store_id}", Store, pk=store_id)
                self.validate_permissions(role, store, "can_decide_on_bid", cursor)
                bids_lock = f"{store.pk}_bids_lock"
                cursor.execute(
                    f"SELECT pg_advisory_xact_lock_shared({hash(bids_lock)});"
                )
                bids = Bid.objects.filter(store=store)
                cache.set_many({f"bid_{store.id}_{bid.id}": bid for bid in bids})
                return bids

    def make_purchase_on_bid(self, request, payload: MakePurchaseOnBidSchemaIn):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{payload.store_id}", Store, pk=payload.store_id)
                bids_lock = f"{payload.store_id}_bids_lock"
                cursor.execute(f"SELECT pg_advisory_xact_lock({hash(bids_lock)});")
                bid = get_or_set_cache(f"bid_{store.id}_{payload.bid_id}", Bid, pk=payload.bid_id)
                if not bid.can_purchase:
                    raise HttpError(
                        400, "Bid has not been accepted by all managers or owners"
                    )
                product = bid.product
                if product.quantity < bid.quantity:
                    raise HttpError(400, "Insufficient quantity of product in store")
                product.quantity -= bid.quantity
                price = bid.price
                product.save()
                #bid.delete()  # delete bid after purchase
                #bid is not deleted to keep track of proudcts a bid was put on
        return {"message": "Purchase made successfully", "price": price}

    def get_managers_with_permissions(self, store_id: int, permission: str):
        store = get_or_set_cache(f"store_{store_id}", Store, pk=store_id)
        managers = Manager.objects.filter(store=store)
        cache.set_many({f"manager_{store.id}_{manager.user_id}": manager for manager in managers})
        managers_with_permission = []
        for manager in managers:
            try:
                manager_permissions = get_or_set_cache(f"manager_permissions_{store.id}_{manager.id}",
                                                       ManagerPermission, manager=manager)
                if getattr(manager_permissions, permission):
                    managers_with_permission.append(manager)
            except Http404:
                pass
        return managers_with_permission

    def get_stores_that_manager_or_owner(self, request, user_id: int):
        stores = []
        owners = Owner.objects.filter(user_id=user_id)  #need all stores he manages so cache cannot be used here
        for owner in owners:
            stores.append(owner.store)
            cache.set(f"owner_{owner.store.id}_{owner.user_id}", owner)
        managers = Manager.objects.filter(user_id=user_id)
        for manager in managers:
            stores.append(manager.store)
            cache.set(f"manager_{manager.store.id}_{manager.user_id}", manager)
        return stores

    def get_bids_on_product(self, request, payload: GetBidsOnProductSchema):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock_shared(%s);", [store_lock])
                store = get_or_set_cache(f"store_{payload.store_id}", Store, pk=payload.store_id)
                bids_lock = f"{payload.store_id}_bids_lock"
                cursor.execute(f"SELECT pg_advisory_xact_lock_shared({hash(bids_lock)});")
                bids = Bid.objects.filter(store=store, product__name=payload.product_name)
                cache.set_many({f"bid_{store.id}_{bid.id}": bid for bid in bids})
                return bids
