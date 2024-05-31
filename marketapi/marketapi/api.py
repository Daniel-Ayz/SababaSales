from ninja import NinjaAPI

from ninja.security import django_auth
from users.api import router as users_router
from purchase.api import router as purchase_router
from store.api import router as store_router


api = NinjaAPI()
api.add_router("/users/", users_router)
api.add_router("/stores/", store_router)
api.add_router("/purchase/", purchase_router)
