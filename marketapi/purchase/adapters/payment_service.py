from purchase.interfaces import PaymentServiceInterface
from purchase.models import PaymentMethod


class AbstractPaymentService(PaymentServiceInterface):
    def process_payment(self, payment_method: PaymentMethod) -> dict:
        raise NotImplementedError("The payment service is not yet implemented.")
