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
@router.get("/purchase/{purchase_id}", response=PurchaseSchema)
def get_purchase_history(request, user_id: int):
    return pc.get_purchase_history(request, user_id)
    

# -------------------- Make Purchase --------------------

@router.post("/purchase/{cart_id}", response=PurchaseSchema)
def make_purchase_of_all_products_in_cart(request, user_id: int, cart_id: int):
    return pc.make_purchase_of_all_products_in_cart(request, user_id, cart_id)
    
