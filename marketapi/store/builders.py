from abc import ABC, abstractmethod

from schemas import ManagerPermissionSchema, ManagerSchema


class ManagerPermissionBuilder(ABC):
    @abstractmethod
    def with_can_add_product(self):
        pass

    @abstractmethod
    def with_can_edit_product(self):
        pass

    @abstractmethod
    def with_can_delete_product(self):
        pass

    @abstractmethod
    def build(self) -> ManagerPermissionSchema:
        """Builds and returns the ManagerPermissionSchema object."""
        pass


class ConcreteManagerPermissionBuilder(ManagerPermissionBuilder):
    def __init__(self):
        self.permissions = {}  # Dictionary to store set permissions

    def with_can_add_product(self):
        self.permissions["can_add_product"] = True

    def with_can_edit_product(self):
        self.permissions["can_edit_product"] = True

    def with_can_delete_product(self):
        self.permissions["can_delete_product"] = True

    def build(self) -> ManagerPermissionSchema:
        return ManagerPermissionSchema(
            **self.permissions,
        )


def create_full_manager_permissions(manager_schema):
    builder = ManagerPermissionBuilder()
    builder.with_can_add_product()
    builder.with_can_edit_product()

    return builder.build()


# manager_schema = ManagerSchema()
# full_manager_permissions = create_full_manager_permissions(manager_schema)
