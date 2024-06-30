from django.contrib import admin

from .models import *

admin.site.register(Store)
admin.site.register(Role)
admin.site.register(Owner)
admin.site.register(Manager)
admin.site.register(ManagerPermission)
admin.site.register(StoreProduct)
admin.site.register(DiscountBase)
admin.site.register(Bid)
admin.site.register(CompositePurchasePolicy)
admin.site.register(ConditionalPurchasePolicy)
admin.site.register(SimplePurchasePolicy)
admin.site.register(PurchasePolicyBase)
admin.site.register(CompositeDiscount)
admin.site.register(ConditionalDiscount)
admin.site.register(SimpleDiscount)
