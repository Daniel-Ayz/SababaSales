from django.db import models


class Store(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Role(models.Model):
    user_id = models.IntegerField()

    class Meta:
        abstract = True


class Owner(Role):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='owners')
    is_founder = models.BooleanField(default=False, unique=True)
    assigned_by = models.ForeignKey('self', on_delete=models.CASCADE, related_name='assigned_owners')
    #because there is a related name we get both who assigned the owner and who else the owner assigned


class Manager(Role):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='managers')
    assigned_by = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='assigned_managers')


class ManagerPermission(models.Model):
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, related_name='manager_permissions')
    can_add_product = models.BooleanField(default=False)
    can_edit_product = models.BooleanField(default=False)
    can_delete_product = models.BooleanField(default=False)


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


class DiscountPolicy(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='discount_policies')
    min_items = models.IntegerField(null=True, blank=True)  # Optional
    min_price = models.FloatField(null=True, blank=True)  # Optional
    discount = models.FloatField()

    def __str__(self):
        return f"Discount: {self.discount}%"
