from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from polymorphic.models import PolymorphicModel


class Store(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Role(models.Model):
    user_id = models.IntegerField()
    store = models.ForeignKey(Store, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Owner(Role):
    #store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='owners')
    is_founder = models.BooleanField(default=False)
    assigned_by = models.ForeignKey('self', on_delete=models.CASCADE, related_name='assigned_owners', null=True,
                                    blank=True)
    #because there is a related name we get both who assigned the owner and who else the owner assigned


class Manager(Role):
    #store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='managers')
    assigned_by = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='assigned_managers')


class ManagerPermission(models.Model):
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, related_name='manager_permissions')
    can_add_product = models.BooleanField(default=False)
    can_edit_product = models.BooleanField(default=False)
    can_delete_product = models.BooleanField(default=False)
    can_add_discount_policy = models.BooleanField(default=False)
    can_add_purchase_policy = models.BooleanField(default=False)
    can_remove_discount_policy = models.BooleanField(default=False)
    can_remove_purchase_policy = models.BooleanField(default=False)


class PurchasePolicy(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='purchase_policies')
    max_items_per_purchase = models.IntegerField(null=True, blank=True)  # Optional
    min_items_per_purchase = models.IntegerField(null=True, blank=True)  # Optional

    def __str__(self):
        policy_text = ""
        if self.max_items_per_purchase:
            policy_text += f"Max items per purchase: {self.max_items_per_purchase}"
        if self.min_items_per_purchase:
            if policy_text:
                policy_text += " & "
            policy_text += f"Min items per purchase: {self.min_items_per_purchase}"
        return policy_text or "No restrictions"


# class DiscountPolicy(models.Model):
#     store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='discount_policies')
#     min_items = models.IntegerField(null=True, blank=True)  # Optional
#     min_price = models.FloatField(null=True, blank=True)  # Optional
#
#     def __str__(self):
#         policy_text = ""
#         if self.min_items:
#             policy_text += f"Min items: {self.min_items}"
#         if self.min_price:
#             if policy_text:
#                 policy_text += " & "
#             policy_text += f"Min price: {self.min_price}"
#         return policy_text or "No restrictions"


class StoreProduct(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='store_products')
    initial_price = models.FloatField()
    quantity = models.IntegerField()
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class DiscountBase(PolymorphicModel):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    #discount_type = models.CharField(max_length=50)
    is_root = models.BooleanField(default=False)


class SimpleDiscount(DiscountBase):
    percentage = models.FloatField()
    applicable_products = models.ManyToManyField(StoreProduct, related_name='simple_discounts')
    applicable_categories = models.TextField(null=True, blank=True)


class ConditionalDiscount(DiscountBase):
    #condition_name = models.CharField(max_length=255)
    discount = models.ForeignKey("DiscountBase", on_delete=models.CASCADE, related_name='conditional_discounts')




@receiver(pre_delete, sender=ConditionalDiscount)
def delete_associated_discount(sender, instance, **kwargs):
    if instance.discount:
        instance.discount.delete()


class CompositeDiscount(DiscountBase):
    discounts = models.ManyToManyField("DiscountBase", related_name='composite_discounts')
    combine_function = models.CharField(max_length=50)
    #conditions = models.TextField(null=True, blank=True)

class Condition(models.Model):
    applies_to = models.CharField(max_length=255) #product, category, time, age, price
    name_of_apply = models.CharField(max_length=255) #name of the product, category, etc.
    condition = models.CharField(max_length=255) #greater than, less than, equal
    value = models.FloatField()
    discount = models.ForeignKey(DiscountBase, on_delete=models.CASCADE, related_name='conditions')

    def __str__(self):
        return "condition for " + self.applies_to + " " + self.name_of_apply + " " + self.condition + " " + self.value


@receiver(pre_delete, sender=CompositeDiscount)
def cascade_delete_discounts(sender, instance, **kwargs):
    # Delete all related discounts
    for discount in instance.discounts.all():
        discount.delete()
