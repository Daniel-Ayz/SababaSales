from django.core.cache import cache
from django.db import models
from django.db.models.signals import pre_delete, post_save, post_delete
from django.dispatch import receiver
from polymorphic.models import PolymorphicModel


class Store(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

@receiver(post_delete, sender=Store)
def delete_store_cache(sender, instance, **kwargs):
    cache_key_store = f"store_{instance.id}"
    cache.delete(cache_key_store)

@receiver(post_save, sender=Store)
def save_store_cache(sender, instance, **kwargs):
    cache_key_store = f"store_{instance.id}"
    cache.set(cache_key_store, instance)


class Role(PolymorphicModel):
    user_id = models.IntegerField()
    store = models.ForeignKey(Store, on_delete=models.CASCADE)


class Owner(Role):
    # store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='owners')
    is_founder = models.BooleanField(default=False)
    assigned_by = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="assigned_owners",
        null=True,
        blank=True,
    )
    # because there is a related name we get both who assigned the owner and who else the owner assigned


@receiver(post_delete, sender=Owner)
def delete_owner_cache(sender, instance, **kwargs):
    cache_key_owner = f"owner_{instance.store.id}_{instance.user_id}"
    cache.delete(cache_key_owner)

@receiver(post_save, sender=Owner)
def save_owner_cache(sender, instance, **kwargs):
    cache_key_owner = f"owner_{instance.store.id}_{instance.user_id}"
    cache.set(cache_key_owner, instance)


class Manager(Role):
    # store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='managers')
    assigned_by = models.ForeignKey(
        Owner, on_delete=models.CASCADE, related_name="assigned_managers"
    )


@receiver(post_delete, sender=Manager)
def delete_manager_cache(sender, instance, **kwargs):
    cache_key_manager = f"manager_{instance.store.id}_{instance.user_id}"
    cache.delete(cache_key_manager)

@receiver(post_save, sender=Manager)
def save_manager_cache(sender, instance, **kwargs):
    cache_key_manager = f"manager_{instance.store.id}_{instance.user_id}"
    cache.set(cache_key_manager, instance)


class ManagerPermission(models.Model):
    manager = models.ForeignKey(
        Manager, on_delete=models.CASCADE, related_name="manager_permissions"
    )
    can_add_product = models.BooleanField(default=False)
    can_edit_product = models.BooleanField(default=False)
    can_delete_product = models.BooleanField(default=False)
    can_add_discount_policy = models.BooleanField(default=False)
    can_add_purchase_policy = models.BooleanField(default=False)
    can_remove_discount_policy = models.BooleanField(default=False)
    can_remove_purchase_policy = models.BooleanField(default=False)
    can_decide_on_bid = models.BooleanField(default=False)

@receiver(post_delete, sender=ManagerPermission)
def delete_manager_permission_cache(sender, instance, **kwargs):
    cache_key_manager_permissions = f"manager_permissions_{instance.manager.store.id}_{instance.manager.user_id}"
    cache.delete(cache_key_manager_permissions)

@receiver(post_save, sender=ManagerPermission)
def save_manager_permission_cache(sender, instance, **kwargs):
    cache_key_manager_permissions = f"manager_permissions_{instance.manager.store.id}_{instance.manager.user_id}"
    cache.set(cache_key_manager_permissions, instance)



class StoreProduct(models.Model):
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="store_products"
    )
    initial_price = models.FloatField()
    quantity = models.IntegerField()
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    # added link to picture - not mandatory
    image_link = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

@receiver(post_delete, sender=StoreProduct)
def delete_store_product_cache(sender, instance, **kwargs):
    cache_key_store_product = f"store_product_{instance.store.id}_{instance.name}"
    cache.delete(cache_key_store_product)

@receiver(post_save, sender=StoreProduct)
def save_store_product_cache(sender, instance, **kwargs):
    cache_key_store_product = f"store_product_{instance.store.id}_{instance.name}"
    cache.set(cache_key_store_product, instance)


class DiscountBase(PolymorphicModel):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    # discount_type = models.CharField(max_length=50)
    is_root = models.BooleanField(default=False)


class SimpleDiscount(DiscountBase):
    percentage = models.FloatField()
    applicable_products = models.ManyToManyField(
        StoreProduct, related_name="simple_discounts"
    )
    applicable_categories = models.TextField(null=True, blank=True)

@receiver(post_delete, sender=SimpleDiscount)
def delete_discount_cache(sender, instance, **kwargs):
    cache_key_discount = f"discount_{instance.store.id}_{instance.id}"
    cache.delete(cache_key_discount)

@receiver(post_save, sender=SimpleDiscount)
def save_discount_cache(sender, instance, **kwargs):
    cache_key_discount = f"discount_{instance.store.id}_{instance.id}"
    cache.set(cache_key_discount, instance)


class ConditionalDiscount(DiscountBase):
    # condition_name = models.CharField(max_length=255)
    discount = models.ForeignKey(
        "DiscountBase", on_delete=models.CASCADE, related_name="conditional_discounts"
    )


@receiver(pre_delete, sender=ConditionalDiscount) #this is pre because before deleting we want to delete the cache of the condition
def delete_associated_discount(sender, instance, **kwargs):
    if instance.discount:
        instance.discount.delete()
    cache_key_conditional_discount = f"discount_{instance.store.id}_{instance.id}"
    cache.delete(cache_key_conditional_discount)


@receiver(post_save, sender=ConditionalDiscount)
def save_conditional_discount_cache(sender, instance, **kwargs):
    cache_key_conditional_discount = f"discount_{instance.store.id}_{instance.id}"
    cache.set(cache_key_conditional_discount, instance)



class CompositeDiscount(DiscountBase):
    discounts = models.ManyToManyField(
        "DiscountBase", related_name="composite_discounts"
    )
    combine_function = models.CharField(max_length=50)
    # conditions = models.TextField(null=True, blank=True)


@receiver(pre_delete, sender=CompositeDiscount)
def cascade_delete_discounts(sender, instance, **kwargs):
    # Delete all related discounts
    for discount in instance.discounts.all():
        discount.delete()
    cache_key_composite_discount = f"discount_{instance.store.id}_{instance.id}"
    cache.delete(cache_key_composite_discount)

@receiver(post_save, sender=CompositeDiscount)
def save_composite_discount_cache(sender, instance, **kwargs):
    cache_key_composite_discount = f"discount_{instance.store.id}_{instance.id}"
    cache.set(cache_key_composite_discount, instance)


class Condition(models.Model):
    applies_to = models.CharField(max_length=255)  # product, category, time, age, price
    name_of_apply = models.CharField(
        max_length=255
    )  # name of the product, category, etc.
    condition = models.CharField(max_length=255)  # greater than, less than, equal
    value = models.FloatField()
    discount = models.ForeignKey(
        DiscountBase,
        on_delete=models.CASCADE,
        related_name="conditions",
        null=True,
        blank=True,
    )
    purchase_policy = models.ForeignKey(
        "PurchasePolicyBase",
        on_delete=models.CASCADE,
        related_name="conditions",
        null=True,
        blank=True,
    )

    def __str__(self):
        return (
                "condition for "
                + self.applies_to
                + " "
                + self.name_of_apply
                + " "
                + self.condition
                + " "
                + self.value
        )

#no point in caching conditions because we always need all the condiotions for a discount or purchase policy and we need to make sure that none are missing
# @receiver(post_delete, sender=Condition)
# def delete_condition_cache(sender, instance, **kwargs):
#     if instance.discount:
#         cache_key_condition_discount = f"condition_discount_{instance.discount.store.id}_{instance.discount.id}"
#         cache.delete(cache_key_condition_discount)
#     elif instance.purchase_policy:
#         cache_key_condition_purchase_policy = f"condition_purchase_policy_{instance.purchase_policy.store.id}_{instance.purchase_policy.id}"
#         cache.delete(cache_key_condition_purchase_policy)
#
# @receiver(post_save, sender=Condition)
# def save_condition_cache(sender, instance, **kwargs):
#     if instance.discount:
#         cache_key_condition_discount = f"condition_discount_{instance.discount.store.id}_{instance.discount.id}"
#         cache.set(cache_key_condition_discount, instance)
#     elif instance.purchase_policy:
#         cache_key_condition_purchase_policy = f"condition_purchase_policy_{instance.purchase_policy.store.id}_{instance.purchase_policy.id}"
#         cache.set(cache_key_condition_purchase_policy, instance)



class PurchasePolicyBase(PolymorphicModel):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    is_root = models.BooleanField(default=False)


class SimplePurchasePolicy(PurchasePolicyBase):
    pass  # no additional fields because this model actually just represents the condition

@receiver(pre_delete, sender=SimplePurchasePolicy)
def delete_simple_purchase_policy(sender, instance, **kwargs):
    cache_key_simple_purchase_policy = f"purchase_policy_{instance.store.id}_{instance.id}"
    cache.delete(cache_key_simple_purchase_policy)

@receiver(post_save, sender=SimplePurchasePolicy)
def save_simple_purchase_policy(sender, instance, **kwargs):
    cache_key_simple_purchase_policy = f"purchase_policy_{instance.store.id}_{instance.id}"
    cache.set(cache_key_simple_purchase_policy, instance)


class ConditionalPurchasePolicy(PurchasePolicyBase):
    restriction = models.ForeignKey(
        PurchasePolicyBase,
        on_delete=models.CASCADE,
        related_name="restriction_policies",
    )
    condition = models.ForeignKey(
        PurchasePolicyBase, on_delete=models.CASCADE, related_name="condition_policies"
    )


@receiver(pre_delete, sender=ConditionalPurchasePolicy)
def delete_associated_condition_restriction(sender, instance, **kwargs):
    instance.restriction.delete()
    instance.condition.delete()
    cache_key_conditional_purchase_policy = f"purchase_policy_{instance.store.id}_{instance.id}"
    cache.delete(cache_key_conditional_purchase_policy)

@receiver(post_save, sender=ConditionalPurchasePolicy)
def save_conditional_purchase_policy(sender, instance, **kwargs):
    cache_key_conditional_purchase_policy = f"purchase_policy_{instance.store.id}_{instance.id}"
    cache.set(cache_key_conditional_purchase_policy, instance)


class CompositePurchasePolicy(PurchasePolicyBase):
    policies = models.ManyToManyField(
        PurchasePolicyBase, related_name="composite_purchase_policies"
    )
    combine_function = models.CharField(max_length=50)


@receiver(pre_delete, sender=CompositePurchasePolicy)
def cascade_delete_policies(sender, instance, **kwargs):
    # Delete all related policies
    for policy in instance.policies.all():
        policy.delete()
    cache_key_composite_purchase_policy = f"purchase_policy_{instance.store.id}_{instance.id}"
    cache.delete(cache_key_composite_purchase_policy)

@receiver(post_save, sender=CompositePurchasePolicy)
def save_composite_purchase_policy(sender, instance, **kwargs):
    cache_key_composite_purchase_policy = f"purchase_policy_{instance.store.id}_{instance.id}"
    cache.set(cache_key_composite_purchase_policy, instance)


class Bid(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    product = models.ForeignKey(StoreProduct, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()
    accepted_by = models.ManyToManyField(Role, related_name="accepted_bids", blank=True)
    user_id = models.IntegerField()  # the user who made the bid
    can_purchase = models.BooleanField(default=False)
    purchased = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} bid in {self.store.name} store"

@receiver(post_delete, sender=Bid)
def delete_bid_cache(sender, instance, **kwargs):
    cache_key_bid = f"bid_{instance.store.id}_{instance.id}"
    cache.delete(cache_key_bid)

@receiver(post_save, sender=Bid)
def save_bid_cache(sender, instance, **kwargs):
    cache_key_bid = f"bid_{instance.store.id}_{instance.id}"
    cache.set(cache_key_bid, instance)
