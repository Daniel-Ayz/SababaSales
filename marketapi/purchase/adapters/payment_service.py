from purchase.interfaces import PaymentServiceInterface
from purchase.models import PaymentMethod


class AbstractPaymentService(PaymentServiceInterface):
    def process_payment(self, payment_method, flag: PaymentMethod) -> dict:
        return not flag
