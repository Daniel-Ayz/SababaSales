from abc import ABC, abstractmethod
from purchase.models import PaymentMethod
from purchase.models import DeliveryMethod


class PaymentServiceInterface(ABC):
    @abstractmethod
    def process_payment(self, payment_method: PaymentMethod) -> dict:
        pass


class DeliveryServiceInterface(ABC):
    @abstractmethod
    def create_shipment(self, delivery_method: DeliveryMethod) -> dict:
        pass
