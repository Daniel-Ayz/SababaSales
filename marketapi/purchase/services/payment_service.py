from purchase.interfaces import PaymentServiceInterface
from purchase.models import PaymentMethod
import requests


class AbstractPaymentService(PaymentServiceInterface):
    def process_payment(self, payment_details: PaymentMethod) -> dict:
        url = "https://damp-lynna-wsep-1984852e.koyeb.app/"

        month = payment_details.expiration_date.split("/")[0]
        year = payment_details.expiration_date.split("/")[1]

        payload = {
            "action_type": "pay",
            "amount": payment_details.total_price,
            "currency": payment_details.currency,
            "card_number": payment_details.credit_card_number,
            "month": month,
            "year": year,
            "holder": payment_details.holder,
            "ccv": payment_details.security_code,
            "id": payment_details.holder_identification_number,
        }
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            result = response.json()
            return {"result": True, "transaction_id": result.get("transaction_id", -1)}
        else:
            return {"result": False, "transaction_id": -1}

    def cancel_payment(self, transaction_id: int) -> dict:
        url = "https://damp-lynna-wsep-1984852e.koyeb.app/"
        payload = {"action_type": "cancel_pay", "transaction_id": transaction_id}
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            result = response.json()
            return {"result": result.get("result", -1) == 1}
        else:
            return {"result": False}
