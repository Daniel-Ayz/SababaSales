from typing import List

from purchase.purchase_controller import purchaseController
from purchase.schemas import PurchaseHistorySchema

import warnings

warnings.filterwarnings("ignore", category=UserWarning)


from ninja import Router

from django.shortcuts import get_object_or_404


router = Router()

pc = purchaseController()


# -------------------- Get history --------------------
@router.get("/{user_id}/get_purchase_history", response=List[PurchaseHistorySchema])
def get_purchase_history(request, user_id: int):
    return pc.get_purchase_history(request, user_id)


# -------------------- Get purchase receipt --------------------
@router.get("/{purchase_id}/get_purchase_receipt", response=PurchaseHistorySchema)
def get_purchase_receipt(request, purchase_id: int):
    return pc.get_purchase_receipt(request, purchase_id)


# -------------------- Make Purchase --------------------

@router.post("/{user_id}/{cart_id}/make_purchase")
def make_purchase(request, user_id, cart_id: int):
    return pc.make_purchase(request, user_id, cart_id)


# -------------------- Make Bid Purchase --------------------

@router.post("/{user_id}/{store_id}/{bid_id}/make_bid_purchase")
def make_bid_purchase(request, user_id: int, store_id: int, bid_id: int):
    return pc.purchase_bid(request, user_id, store_id, bid_id)