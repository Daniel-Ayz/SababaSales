from django.contrib import admin

from .models import *

admin.site.register(Purchase)
admin.site.register(PaymentMethod)
admin.site.register(HistoryBasket)
admin.site.register(HistoryBasketProduct)
