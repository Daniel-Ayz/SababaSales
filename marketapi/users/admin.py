from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser
from .models import Notification
from .models import Cart
from .models import Basket

# Register your models here.
admin.site.register(CustomUser, UserAdmin)
admin.site.register(Notification)
admin.site.register(Cart)
admin.site.register(Basket)
