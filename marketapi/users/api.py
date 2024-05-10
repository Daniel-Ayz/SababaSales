from ninja import Router

router = Router()


@router.get("/")
def hello_world(request):
    return {"msg": "hello from users!"}


@router.get("/{user_id}")
def hello_from_user(request, user_id: int):
    return {"msg": f"hello from {user_id}!"}
