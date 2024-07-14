def init_online_counter():
    from .consumers import reset_all_online_count

    reset_all_online_count()
    print("[+] All users online count reset to 0")


def init_fake_data_users():
    from .models import CustomUser

    user = CustomUser.objects.filter(username="Yishay_Butzim")
    if not user:
        print("[!] Creating fake data for users...")
        from .usercontroller import UserController

        uc = UserController()
        uc.create_fake_data()
        print("[+] Fake data for users created")
    else:
        print("[*] Fake data for users already exists")


def init_fake_data_store():

    from store.models import Store

    store = Store.objects.filter(name="Hummus Heaven")
    if not store:
        print("[!] Creating fake data for products...")
        from store.store_controller import StoreController

        sc = StoreController()
        sc.create_fake_data()
        print("[+] Fake data for products created")
    else:
        print("[*] Fake data for products already exists")


def insure_admin_user():
    from .models import CustomUser

    admin = CustomUser.objects.filter(is_superuser=True)
    if not admin:
        print("[!] Creating admin user...")
        CustomUser.objects.create_superuser("admin", password="admin")
        print("[+] Admin user created")
    else:
        print("[*] Admin user already exists")


def initialize():
    print("Initializing the server...")
    # reset online counters to 0 for all users
    init_online_counter()

    # check if fake data for users is created -> if not create it
    init_fake_data_users()

    # check if fake data for products is created -> if not create it
    init_fake_data_store()

    # check if we have admin user -> if not create it
    insure_admin_user()
    print("[+] Initialization complete")
