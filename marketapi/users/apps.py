from django.apps import AppConfig
import sys


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    # From stackoverflow https://stackoverflow.com/a/49035207
    # This function is called when the server starts -
    # only when run server is called (and not when making migrations, migrate, shell, etc. are called)
    def ready(self):
        if "runserver" not in sys.argv:
            return True

        from .consumers import reset_all_online_count

        reset_all_online_count()
        print("All users online count reset to 0")
