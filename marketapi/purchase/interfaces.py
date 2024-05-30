from abc import ABC, abstractmethod
from purchase.models import PaymentMethod


class PaymentServiceInterface(ABC):
    @abstractmethod
    def process_payment(self, payment_method: PaymentMethod) -> dict:
        pass


class DeliveryServiceInterface(ABC):
    @abstractmethod
    def create_shipment(self, address: str, item_quantity: float, **kwargs) -> dict:
        pass
