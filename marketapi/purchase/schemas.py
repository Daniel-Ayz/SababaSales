from ninja import Schema
from ninja.orm import ModelSchema

from .models import Purchase

# -------------------- Purchase --------------------


class PurchaseSchema(ModelSchema):
    class Meta:
        model = Purchase
        fields = "__all__"
