import json
from typing import List, Union

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError

from .discount import SimpleDiscountClass, ConditionalDiscountClass, CompositeDiscountClass
from .models import Store, Owner, Manager, ManagerPermission, PurchasePolicy, StoreProduct, SimpleDiscount, \
    ConditionalDiscount, CompositeDiscount, DiscountBase, Condition
from .schemas import StoreSchemaIn, OwnerSchemaIn, ManagerPermissionSchemaIn, PurchasePolicySchemaIn, \
    StoreProductSchemaIn, ManagerSchemaIn, RoleSchemaIn, PurchaseStoreProductSchema, RemoveOwnerSchemaIn, \
    RemoveManagerSchemaIn, SimpleDiscountSchemaIn, CompositeDiscountSchemaIn, \
    ConditionalDiscountSchemaIn, RemoveDiscountSchemaIn, ConditionalDiscountSchemaOut, CompositeDiscountSchemaOut, \
    FilterSearchSchema, SearchSchema

router = Router()


def get_list_from_string(conditions):
    jsonDec = json.decoder.JSONDecoder()
    return jsonDec.decode(conditions)


class StoreController:
    def get_store(self, request, store_id: int):
        return get_object_or_404(Store, pk=store_id)
        # return {"id": store.id,"created_at" : store.created_at, "name": store.name, "description": store.description, "is_active": store.is_active}

    # @router.get("/stores/{store_id}", response=StoreSchemaOut)
    # async def get_store(request, store_id: int):
    #     return await aget_object_or_404(Store, pk=store_id)

    def create_store(self, request, payload: StoreSchemaIn, user_id: int):
        if Store.objects.filter(name=payload.name).exists():
            raise HttpError(403, "Store with this name already exists")
        store = Store.objects.create(**payload.dict(), is_active=True)
        Owner.objects.create(user_id=user_id, store=store, is_founder=True)
        return {"store_id": store.id}

    # @router.post("/stores")
    # async def create_store(request, payload: StoreSchemaIn, user_id: int):
    #     if Store.objects.filter(name=payload.name).exists():
    #         raise HttpError(403, "Store with this name already exists")
    #     store = await Store.objects.acreate(**payload.dict(), is_active=True)
    #     await Owner.objects.acreate(
    #         user_id=user_id,
    #         store=store,
    #         is_founder=True
    #     )
    #     return {"store_id": store.id}

    def get_stores(self, request):
        return Store.objects.all()

    # @router.get("/stores", response=List[StoreSchemaOut])
    # async def get_stores(request):
    #     return await Store.objects.all()

    def assign_owner(self, request, payload: OwnerSchemaIn):
        store = get_object_or_404(Store, pk=payload.store_id)
        assigning_owner = get_object_or_404(
            Owner, user_id=payload.assigned_by, store=store
        )
        if Owner.objects.filter(user_id=payload.user_id, store=store).exists():
            raise HttpError(400, "User is already an owner")

        owner = Owner.objects.create(
            user_id=payload.user_id,
            assigned_by=assigning_owner,
            store=store,
            is_founder=False,
        )
        return {"message": "Owner assigned successfully"}

    # @router.post("/stores/{store_id}/assign_owner")
    # async def assign_owner(request, payload: OwnerSchemaIn):
    #     store = await aget_object_or_404(Store, pk=payload.store_id)
    #     assigning_owner = await aget_object_or_404(Owner, user_id=payload.assigned_by, store=store)
    #     if await Owner.objects.filter(user_id=payload.user_id, store=store).exists():
    #         raise HttpError(400, "User is already an owner")
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
    #         raise HttpError(403, "Owner can only be removed by the owner who assigned them")
    #
    #     await removed_owner.adelete()
    #     return {"message": "Owner removed success"}

    def remove_owner(self, request, payload: RemoveOwnerSchemaIn):
        store = get_object_or_404(Store, pk=payload.store_id)
        removing_owner = get_object_or_404(
            Owner, user_id=payload.removed_by, store=store
        )
        removed_owner = get_object_or_404(Owner, user_id=payload.user_id, store=store)

        if removed_owner.assigned_by != removing_owner:
            raise HttpError(
                403, "Owner can only be removed by the owner who assigned them"
            )

        removed_owner.delete()
        return {"message": "Owner removed successfully"}

    def leave_ownership(self, request, payload: RoleSchemaIn):
        store = get_object_or_404(Store, pk=payload.store_id)
        owner = get_object_or_404(Owner, user_id=payload.user_id, store=store)
        if owner.is_founder:
            raise HttpError(400, "Founder cannot leave ownership")

        owner.delete()
        return {"message": "Ownership left successfully"}

    def assign_manager(self, request, payload: ManagerSchemaIn):
        store = get_object_or_404(Store, pk=payload.store_id)
        assigning_owner = get_object_or_404(
            Owner, user_id=payload.assigned_by, store=store
        )
        if Manager.objects.filter(user_id=payload.user_id, store=store).exists():
            raise HttpError(400, "User is already a manager")
        elif Owner.objects.filter(user_id=payload.user_id, store=store).exists():
            raise HttpError(400, "User is already an owner")

            # Check if the assigning user is an owner
        if not Owner.objects.filter(user_id=payload.assigned_by, store=store).exists():
            raise HttpError(403, "Only owners can assign managers")

        manager = Manager.objects.create(
            user_id=payload.user_id, assigned_by=assigning_owner, store=store
        )
        return {"message": "Manager assigned successfully"}

    def remove_manager(self, request, payload: RemoveManagerSchemaIn):
        store = get_object_or_404(Store, pk=payload.store_id)
        removing_owner = get_object_or_404(
            Owner, user_id=payload.removed_by, store=store
        )
        removed_manager = get_object_or_404(
            Manager, user_id=payload.user_id, store=store
        )

        if removed_manager.assigned_by != removing_owner:
            raise HttpError(
                403, "Manager can only be removed by the owner who assigned them"
            )

        removed_manager.delete()
        return {"message": "Manager removed successfully"}

    def assign_manager_permissions(
            self,
            request,
            payload: ManagerPermissionSchemaIn,
            manager: RoleSchemaIn,
            assigning_owner_id: int,
    ):
        store = get_object_or_404(Store, pk=manager.store_id)
        manager = get_object_or_404(Manager, user_id=manager.user_id, store=store)
        if assigning_owner_id != manager.assigned_by.user_id:
            raise HttpError(403, "Only assigning owner can assign permissions")
        try:
            existing_permission, _ = ManagerPermission.objects.update_or_create(
                manager=manager, defaults=payload.dict()
            )
        except Exception as e:
            raise HttpError(500, f"Error assigning permissions: {str(e)}")

        return {"message": "Manager permissions assigned successfully"}

    def get_manager_permissions(self, request, role: RoleSchemaIn, manager_id: int):
        store = get_object_or_404(Store, pk=role.store_id)
        manager = get_object_or_404(Manager, pk=manager_id, store=store)
        permissions = get_object_or_404(ManagerPermission, manager=manager)
        return permissions

    def close_store(self, request, payload: RoleSchemaIn):
        store = get_object_or_404(Store, pk=payload.store_id)
        owner = get_object_or_404(Owner, user_id=payload.user_id, store=store)
        if not owner.is_founder:
            raise HttpError(403, "Only the founder can close the store")

        store.is_active = False
        store.save()

        return {"message": "Store closed successfully"}

    def reopen_store(self, request, payload: RoleSchemaIn):
        store = get_object_or_404(Store, pk=payload.store_id)
        owner = get_object_or_404(Owner, user_id=payload.user_id, store=store)
        if not owner.is_founder:
            raise HttpError(403, "Only the founder can reopen the store")

        store.is_active = True
        store.save()

        return {"message": "Store reopened successfully"}

    def get_owners(self, request, payload: RoleSchemaIn):
        store = get_object_or_404(Store, pk=payload.store_id)
        if not Owner.objects.filter(user_id=payload.user_id, store=store).exists():
            raise HttpError(403, "User is not an owner of the store")

        owners = Owner.objects.filter(store=store)

        return owners

    def get_managers(self, request, payload: RoleSchemaIn):
        store = get_object_or_404(Store, pk=payload.store_id)
        if not Owner.objects.filter(user_id=payload.user_id, store=store).exists():
            raise HttpError(403, "User is not an owner of the store")

        managers = Manager.objects.filter(store=store)

        return managers

    def add_purchase_policy(
            self, request, role: RoleSchemaIn, payload: PurchasePolicySchemaIn
    ):
        store = get_object_or_404(Store, pk=role.store_id)

        # Check if the user is an owner or manager of the store
        if not Owner.objects.filter(user_id=role.user_id, store=store).exists():
            if not Manager.objects.filter(user_id=role.user_id, store=store).exists():
                raise HttpError(403, "User is not an owner or manager of the store")

            manager = get_object_or_404(Manager, user_id=role.user_id, store=store)
            manager_permissions = get_object_or_404(ManagerPermission, manager=manager)
            if not manager_permissions.can_add_purchase_policy:
                raise HttpError(
                    403, "Manager does not have permission to add purchase policy"
                )

        # Check if a purchase policy already exists for the store
        if PurchasePolicy.objects.filter(store=store).exists():
            raise HttpError(400, "Purchase policy already exists for the store")

        policy = PurchasePolicy.objects.create(store=store, **payload.dict())

        return {"message": "Purchase policy added successfully"}

    def remove_purchase_policy(self, request, store_id: int, role: RoleSchemaIn):
        store = get_object_or_404(Store, pk=store_id)

        # Check if the user is an owner or manager of the store
        if not Owner.objects.filter(user_id=role.user_id, store=store).exists():
            if not Manager.objects.filter(user_id=role.user_id, store=store).exists():
                raise HttpError(403, "User is not an owner or manager of the store")

            manager = get_object_or_404(Manager, user_id=role.user_id, store=store)
            manager_permissions = get_object_or_404(ManagerPermission, manager=manager)
            if not manager_permissions.can_remove_purchase_policy:
                raise HttpError(
                    403, "Manager does not have permission to remove purchase policy"
                )

        # Check if a purchase policy exists for the store
        try:
            policy = PurchasePolicy.objects.get(store=store)
        except PurchasePolicy.DoesNotExist:
            raise HttpError(404, "Purchase policy not found for the store")

        # Delete the purchase policy
        policy.delete()

        return {"message": "Purchase policy removed successfully"}

    def get_purchase_policy(self, request, store_id: int, role: RoleSchemaIn):
        store = get_object_or_404(Store, pk=store_id)
        if not store.is_active:
            if not Owner.objects.filter(user_id=role.user_id, store=store).exists():
                raise HttpError(
                    403, "User is not an owner of the store and the store is closed"
                )

        policies = PurchasePolicy.objects.filter(store=store)

        return policies

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

    # def add_discount_policy(self, request, role: RoleSchemaIn, payload: DiscountBaseSchema):
    #     store = get_object_or_404(Store, pk=role.store_id)
    #
    #     # Check if the user is an owner or manager of the store
    #     if not Owner.objects.filter(user_id=role.user_id, store=store).exists():
    #         if not Manager.objects.filter(user_id=role.user_id, store=store).exists():
    #             raise HttpError(403, "User is not an owner or manager of the store")
    #
    #         manager = get_object_or_404(Manager, user_id=role.user_id, store=store)
    #         manager_permissions = get_object_or_404(ManagerPermission, manager=manager)
    #         if not manager_permissions.can_add_discount_policy:
    #             raise HttpError(403, "Manager does not have permission to change discount policy")
    #
    #     # Check if a discount policy with the same parameters already exists for the store
    #     if DiscountPolicy.objects.filter(store=store, min_items=payload.min_items,
    #                                      min_price=payload.min_price).exists():
    #         raise HttpError(400, "Discount policy with these parameters already exists")
    #
    #     policy = DiscountPolicy.objects.create(
    #         store=store,
    #         **payload.dict()
    #     )
    #
    #     return {"message": "Discount policy added successfully"}

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
            store = get_object_or_404(Store, pk=payload.store_id)
            self.validate_permissions(role, store, "can_add_discount_policy")

        if isinstance(payload, SimpleDiscountSchemaIn):
            return self.add_simple_discount_policy(payload)
        elif isinstance(payload, CompositeDiscountSchemaIn):
            return self.add_composite_discount_policy(payload)
        elif isinstance(payload, ConditionalDiscountSchemaIn):
            return self.add_conditional_discount_policy(payload)

    def add_simple_discount_policy(self, payload: SimpleDiscountSchemaIn):
        store = get_object_or_404(Store, pk=payload.store_id)

        # if SimpleDiscount.objects.filter(store=store, percentage=payload.percentage).exists():
        #     raise HttpError(400, "Simple discount policy with these parameters already exists")

        # if SimpleDiscount.objects.filter(store=store, percentage=payload.percentage,
        #                                  applicable_products__in=applicable_products).exists():
        #     raise HttpError(400, "Simple discount policy with these parameters already exists")
        discount = SimpleDiscount.objects.create(
            store=store,
            is_root=payload.is_root,
            percentage=payload.percentage,
            applicable_categories=json.dumps(payload.applicable_categories),
        )
        if payload.applicable_products:
            applicable_products = StoreProduct.objects.filter(
                store=store, name__in=payload.applicable_products
            )
            discount.applicable_products.set(applicable_products)

        return {
            "message": "Simple discount policy added successfully",
            "discount": discount,
        }

    def add_conditional_discount_policy(self, payload: ConditionalDiscountSchemaIn):
        store = get_object_or_404(Store, pk=payload.store_id)

        # if ConditionalDiscount.objects.filter(store=store, discount_type=payload.discount_type).exists():
        #     raise HttpError(400, "Conditional discount policy with these parameters already exists")
        base_discount = (self.add_discount_policy(None, None, payload.discount)).get(
            "discount"
        )
        discount = ConditionalDiscount.objects.create(
            is_root=payload.is_root,
            store=store,
            discount=base_discount
        )

        condition = Condition.objects.create(
            applies_to=payload.condition.applies_to,
            name_of_apply=payload.condition.name_of_apply,
            condition=payload.condition.condition,
            value=payload.condition.value,
            discount=discount
        )

        return {"message": "Conditional discount policy added successfully", "discount": discount}

    def add_composite_discount_policy(self, payload: CompositeDiscountSchemaIn):
        store = get_object_or_404(Store, pk=payload.store_id)

        # if CompositeDiscount.objects.filter(store=store, discount_type=payload.discount_type).exists():
        #     raise HttpError(400, "Composite discount policy with these parameters already exists")
        discounts = []
        for discount_payload in payload.discounts:
            discounts.append(
                (self.add_discount_policy(None, None, discount_payload)).get("discount")
            )
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
                discount=discount
            )

        return {"message": "Composite discount policy added successfully", "discount": discount}

    def remove_discount_policy(
            self, request, role: RoleSchemaIn, payload: RemoveDiscountSchemaIn
    ):
        store = get_object_or_404(Store, pk=payload.store_id)

        self.validate_permissions(role, store, "can_remove_discount_policy")
        # try:
        #     # Try to get the discount instance by its ID in each subclass
        #     discount_instance = SimpleDiscount.objects.get(pk=payload.discount_id, is_root=True)
        # except ObjectDoesNotExist:
        #     try:
        #         discount_instance = ConditionalDiscount.objects.get(pk=payload.discount_id, is_root=True)
        #     except ObjectDoesNotExist:
        #         try:
        #             discount_instance = CompositeDiscount.objects.get(pk=payload.discount_id, is_root=True)
        #         except ObjectDoesNotExist:
        #             raise HttpError(404, "Discount policy does not exist")

        discount_instance = get_object_or_404(
            DiscountBase, pk=payload.discount_id, is_root=True
        )

        discount_instance.delete()

        return {"message": "Discount policy removed successfully"}

    # def remove_discount_policy(self, request, role: RoleSchemaIn, payload: DiscountPolicySchemaIn):
    #     store = get_object_or_404(Store, pk=role.store_id)
    #
    #     # Check if the user is an owner or manager of the store
    #     if not Owner.objects.filter(user_id=role.user_id, store=store).exists():
    #         if not Manager.objects.filter(user_id=role.user_id, store=store).exists():
    #             raise HttpError(403, "User is not an owner or manager of the store")
    #
    #         manager = get_object_or_404(Manager, user_id=role.user_id, store=store)
    #         manager_permissions = get_object_or_404(ManagerPermission, manager=manager)
    #         if not manager_permissions.can_remove_discount_policy:
    #             raise HttpError(403, "Manager does not have permission to change discount policy")
    #
    #     # Check if a discount policy exists for the store
    #     try:
    #         policy = DiscountPolicy.objects.get(store=store, min_items=payload.min_items, min_price=payload.min_price)
    #     except DiscountPolicy.DoesNotExist:
    #         raise HttpError(404, "Discount policy not found for the store")
    #
    #     # Delete the discount policy
    #     policy.delete()
    #
    #     return {"message": "Discount policy removed successfully"}

    def get_discount_policies(self, request, role: RoleSchemaIn):
        store = get_object_or_404(Store, pk=role.store_id)
        if not store.is_active:
            if not Owner.objects.filter(user_id=role.user_id, store=store).exists():
                raise HttpError(
                    403, "User is not an owner of the store and the store is closed"
                )

        return DiscountBase.objects.filter(store=store, is_root=True)

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

    def validate_permissions(self, role: RoleSchemaIn, store: Store, permission: str):
        if not Owner.objects.filter(user_id=role.user_id, store=store).exists():
            if not Manager.objects.filter(user_id=role.user_id, store=store).exists():
                raise HttpError(403, "User is not an owner or manager of the store")

            manager = get_object_or_404(Manager, user_id=role.user_id, store=store)
            manager_permissions = get_object_or_404(ManagerPermission, manager=manager)
            if not getattr(manager_permissions, permission):
                raise HttpError(
                    403, "Manager does not have permission to perform this action"
                )

    def add_product(self, request, role: RoleSchemaIn, payload: StoreProductSchemaIn):
        store = get_object_or_404(Store, pk=role.store_id)

        self.validate_permissions(role, store, "can_add_product")
        # if not Owner.objects.filter(user_id=role.user_id, store=store).exists():
        #     if not Manager.objects.filter(user_id=role.user_id, store=store).exists():
        #         raise HttpError(403, "User is not an owner or manager of the store")
        #
        #     manager = get_object_or_404(Manager, user_id=role.user_id, store=store)
        #     manager_permissions = get_object_or_404(ManagerPermission, manager=manager)
        #     if not manager_permissions.can_add_product:
        #         raise HttpError(403, "Manager does not have permission to add product")

        all_products = StoreProduct.objects.filter(store=store)
        if payload.name in all_products.values_list("name", flat=True):
            return HttpError(400, "Product with this name already exists in the store")
        if payload.quantity <= 0:
            raise HttpError(400, "Product quantity cannot be 0 or negative")
        if payload.initial_price <= 0:
            raise HttpError(400, "Product price cannot be 0 or negative")

        product = StoreProduct.objects.create(store=store, **payload.dict())

        return {"message": "Product added successfully"}

    def remove_product(self, request, role: RoleSchemaIn, product_name: str):
        store = get_object_or_404(Store, pk=role.store_id)
        self.validate_permissions(role, store, "can_delete_product")

        # Check if the user is an owner or manager of the store
        # if not Owner.objects.filter(user_id=role.user_id, store=store).exists():
        #     if not Manager.objects.filter(user_id=role.user_id, store=store).exists():
        #         raise HttpError(403, "User is not an owner or manager of the store")
        #
        #     manager = get_object_or_404(Manager, user_id=role.user_id, store=store)
        #     manager_permissions = get_object_or_404(ManagerPermission, manager=manager)
        #     if not manager_permissions.can_delete_product:
        #         raise HttpError(403, "Manager does not have permission to delete product")

        # Check if the product exists
        product = get_object_or_404(StoreProduct, store=store, name=product_name)

        # Delete the product
        product.delete()

        return {"message": "Product removed successfully"}

    def edit_product(self, request, role: RoleSchemaIn, payload: StoreProductSchemaIn):
        store = get_object_or_404(Store, pk=role.store_id)

        self.validate_permissions(role, store, "can_edit_product")

        # Check if the user is an owner or manager of the store
        # if not Owner.objects.filter(user_id=role.user_id, store=store).exists():
        #     if not Manager.objects.filter(user_id=role.user_id, store=store).exists():
        #         raise HttpError(403, "User is not an owner or manager of the store")
        #
        #     manager = get_object_or_404(Manager, user_id=role.user_id, store=store)
        #     manager_permissions = get_object_or_404(ManagerPermission, manager=manager)
        #     if not manager_permissions.can_edit_product:
        #         raise HttpError(403, "Manager does not have permission to edit product")

        # Get the product to edit
        product = get_object_or_404(StoreProduct, store=store, name=payload.name)

        # Validate payload
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
        product.save()

        return {"message": "Product edited successfully"}

    def get_products(self, request, store_id: int, role: RoleSchemaIn):
        store = get_object_or_404(Store, pk=store_id)
        if not store.is_active:
            if not Owner.objects.filter(user_id=role.user_id, store=store).exists():
                raise HttpError(
                    403, "User is not an owner of the store and the store is closed"
                )

        products = StoreProduct.objects.filter(store=store)

        return products

    def purchase_product(
            self, request, store_id: int, payload: List[PurchaseStoreProductSchema]
    ):
        if payload is None or len(payload) == 0:
            raise HttpError(400, "No products to purchase")
        store = get_object_or_404(Store, pk=store_id)

        total_items = sum(item.quantity for item in payload)
        products = [
            get_object_or_404(StoreProduct, store=store, name=item.product_name)
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
            {"name": product.name,
             "initial price": product.initial_price,
             "quantity": item.quantity,
             "total quantity": product.initial_price * item.quantity}
            for product, item in zip(products, payload)
        ]
        # Check purchase policy limits
        store_purchase_policy = get_object_or_404(PurchasePolicy, store=store)
        if (
                store_purchase_policy.max_items_per_purchase
                and total_items > store_purchase_policy.max_items_per_purchase
        ):
            raise HttpError(
                400, "Total items exceeds the maximum items per purchase limit"
            )
        if (
                store_purchase_policy.min_items_per_purchase
                and total_items < store_purchase_policy.min_items_per_purchase
        ):
            raise HttpError(
                400, "Total items is less than the minimum items per purchase limit"
            )

        # Apply discount policy
        total_price -= self.calculate_cart_discount(payload, store)

        for item in payload:
            product = get_object_or_404(
                StoreProduct, store=store, name=item.product_name
            )
            if product.quantity < item.quantity:
                raise HttpError(
                    400, f"Insufficient quantity of {product.name} in store"
                )
            product.quantity -= item.quantity
            if product.quantity == 0:
                product.delete()
            else:
                product.save()
        return {
            "message": "Products purchased successfully",
            "total_price": total_price,
            "original_price": original_total_price,
            "original_prices": original_prices,
        }

    def return_products(self, request, store_id: int, payload: List[PurchaseStoreProductSchema]):
        if payload is None or len(payload) == 0:
            raise HttpError(400, "No products to return")
        store = get_object_or_404(Store, pk=store_id)

        for item in payload:
            product = get_object_or_404(StoreProduct, store=store, name=item.product_name)
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
            related_discount = self.get_discount_instance(discount_model.discount, store)
            return ConditionalDiscountClass(condition_name, related_discount, store)
        elif isinstance(discount_model, CompositeDiscount):
            discounts = [self.get_discount_instance(d, store) for d in discount_model.discounts.all()]
            conditions = discount_model.conditions.all()
            return CompositeDiscountClass(discounts, discount_model.combine_function, conditions, store)
        return None

    def calculate_cart_discount(
            self, purchase_products: List[PurchaseStoreProductSchema], store: Store
    ):
        total_discount = 0
        # Retrieve only root discount models to avoid duplicates
        all_discount_models = DiscountBase.objects.filter(is_root=True)
        for discount_model in all_discount_models:
            discount_instance = self.get_discount_instance(discount_model, store)
            if discount_instance:
                discount = discount_instance.apply_discount(purchase_products)
                if discount:
                    total_discount += discount
        return total_discount

    def search_products(self, request, search_query: SearchSchema, filter_query: FilterSearchSchema):
        if search_query.store_id:
            store = get_object_or_404(Store, pk=search_query.store_id)
            if not store.is_active:
                raise HttpError(403, "Store is closed")
            if search_query.product_name and not search_query.category:
                products = StoreProduct.objects.filter(store=store, name__icontains=search_query.product_name)
            elif search_query.category and not search_query.product_name:
                products = StoreProduct.objects.filter(store=store, category__icontains=search_query.category)
            elif search_query.product_name and search_query.category:
                products = StoreProduct.objects.filter(store=store, name__icontains=search_query.product_name,
                                                       category__icontains=search_query.category)
            else:
                products = StoreProduct.objects.filter(store=store)
        else:
            if search_query.product_name and not search_query.category:
                products = StoreProduct.objects.filter(name__icontains=search_query.product_name, store__is_active=True)
            elif search_query.category and not search_query.product_name:
                products = StoreProduct.objects.filter(category__icontains=search_query.category, store__is_ative=True)
            elif search_query.product_name and search_query.category:
                products = StoreProduct.objects.filter(name__icontains=search_query.product_name,
                                                       category__icontains=search_query.category, store__is_active=True)
            else:
                products = StoreProduct.objects.filter(store__is_active=True)

        if filter_query.min_price:
            products = products.filter(initial_price__gte=filter_query.min_price)
        if filter_query.max_price:
            products = products.filter(initial_price__lte=filter_query.max_price)
        if filter_query.min_quantity:
            products = products.filter(quantity__gte=filter_query.min_quantity)
        if filter_query.max_quantity:
            products = products.filter(quantity__lte=filter_query.max_quantity)

        return products

    def create_fake_data(self, request):
        store_data = {
            "Hummus Heaven": {
                "category": "Food",
                "products": ["Classic Hummus", "Spicy Hummus", "Garlic Hummus"],
            },
            "Falafel Fiesta": {
                "category": "Food",
                "products": ["Falafel Wrap", "Falafel Plate", "Falafel Salad"],
            },
            "Startup Nation Tech": {
                "category": "Technology",
                "products": [
                    "Israeli Smartphone",
                    "Kibbutz Laptop",
                    "Jerusalem Smartwatch",
                ],
            },
            "Tel Aviv Trends": {
                "category": "Clothing",
                "products": [
                    "Sabra Designer Dress",
                    "Negev Leather Jacket",
                    "Eilat Running Shoes",
                ],
            },
            "Book Bazaar Israel": {
                "category": "Books",
                "products": [
                    "Hebrew Science Fiction Novel",
                    "Israeli Cookbook",
                    "Zionist Historical Biography",
                ],
            },
            "Toy Town Israel": {
                "category": "Toys",
                "products": [
                    "David Ben-Gurion Action Figure",
                    "Israeli Board Game",
                    "Jerusalem Puzzle Set",
                ],
            },
        }

        stores = []
        store_names = store_data.keys()
        for i in range(1, 7):
            stores.append(
                Store.objects.create(
                    name=store_names[i - 1],
                    description=f"This is a fake store {i}",
                    is_active=True,
                )
            )

        for i in range(0, 6):
            owner = Owner.objects.create(user_id=i, store=stores[i], is_founder=True)
            manager = Manager.objects.create(
                user_id=2 * len(store_names) - i - 1, store=stores[i]
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
                    name=store_data[stores[i]]["products"][j],
                    quantity=10,
                    initial_price=100,
                )
                purchase_policy = PurchasePolicy.objects.create(
                    store=stores[i], max_items_per_purchase=5, min_items_per_purchase=1
                )
                discount = SimpleDiscount.objects.create(
                    store=stores[i],
                    is_root=True,
                    percentage=10,
                    applicable_categories=json.dumps(
                        [store_data[stores[i]]["category"]]
                    ),
                )

        return {"message": "Fake data created successfully"}
