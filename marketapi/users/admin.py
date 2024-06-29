from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *

# Register your models here.
admin.site.register(CustomUser, UserAdmin)
admin.site.register(Notification)
admin.site.register(Cart)
admin.site.register(Basket)
admin.site.register(PaymentInformationUser)
admin.site.register(BasketProduct)
