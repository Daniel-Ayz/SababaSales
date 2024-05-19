from typing import List

from purchase.purchase_controller import purchaseController
from purchase.schemas import PurchaseSchema

import warnings

warnings.filterwarnings("ignore", category=UserWarning)


from ninja import Router

from django.shortcuts import get_object_or_404


router = Router()

pc = purchaseController()


# -------------------- Get history --------------------
@router.get("/{user_id}/get_purchase_history", response=List[PurchaseSchema])
def get_purchase_history(request, user_id: int):
    return pc.get_purchase_history(request, user_id)


# -------------------- Make Purchase --------------------


@router.post("/{cart_id}/make_purchase")
def make_purchase(
    request, cart_id: int, flag_delivery: bool = False, flag_payment: bool = False
):
    return pc.make_purchase(request, cart_id, flag_delivery=False, flag_payment=False)
