from ninja import NinjaAPI

from ninja.security import django_auth
from users.api import router as users_router


api = NinjaAPI(csrf=True)
api.add_router("/users/", users_router)
