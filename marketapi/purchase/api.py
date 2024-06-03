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
@router.get("/{user_id}/get_purchase_history", response=List[PurchaseSchema]) # response should be changed to the correct schema
def get_purchase_history(request, user_id: int):
    return pc.get_purchase_history(request, user_id)

# -------------------- Get purchase receipt --------------------
@router.get("/{purchase_id}/get_purchase_receipt", response=PurchaseSchema) # response should be changed to the correct schema
def get_purchase_receipt(request, purchase_id: int):
    return pc.get_purchase_receipt(request, purchase_id)


# -------------------- Make Purchase --------------------


@router.post("/{user_id}/{cart_id}/make_purchase")
def make_purchase(request, user_id, cart_id: int):
    return pc.make_purchase(
        request, user_id, cart_id, flag_delivery=False, flag_payment=False
    )


# those are for tests
@router.post("/{user_id}/{cart_id}/make_purchase_delivery_fail")
def make_purchase(request, user_id, cart_id: int):
    return pc.make_purchase(request,user_id, cart_id, flag_delivery=True, flag_payment=False)


@router.post("/{user_id}/{cart_id}/make_purchase_payment_fail")
def make_purchase(request, user_id, cart_id: int):
    return pc.make_purchase(
        request, user_id, cart_id, flag_delivery=False, flag_payment=True
    )
