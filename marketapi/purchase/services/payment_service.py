from purchase.interfaces import PaymentServiceInterface
from purchase.models import PaymentMethod
import requests

from ninja.errors import HttpError


class AbstractPaymentService(PaymentServiceInterface):
    def process_payment(self, payment_details: PaymentMethod) -> dict:
        url = "https://damp-lynna-wsep-1984852e.koyeb.app/"

        expiration_date = payment_details["expiration_date"]
        tuple = expiration_date.split("/")
        if len(tuple) != 2:
            raise HttpError(400, "Invalid Payment Information")
        month, year = tuple

        if (
            payment_details["holder"] == ""
            or payment_details["holder_identification_number"] == ""
            or payment_details["currency"] == ""
            or payment_details["credit_card_number"] == ""
            or payment_details["expiration_date"] == ""
            or payment_details["security_code"] == ""
            or payment_details["total_price"] == 0
            or month == ""
            or year == ""
        ):
            raise HttpError(400, "Invalid Payment Information")
        year = "20" + year
        handshake_payload = {
            "action_type": "handshake",
        }
        response = requests.post(url, data=handshake_payload)

        if response.status_code != 200:
            raise HttpError(400, "Could not connect to payment service")
        
        payload = {
            "action_type": "pay",
            "amount": str(payment_details["total_price"]),
            "currency": payment_details["currency"],
            "card_number": payment_details["credit_card_number"],
            "month": month,
            "year": year,
            "holder": payment_details["holder"],
            "cvv": payment_details["security_code"],
            "id": payment_details["holder_identification_number"],
        }
        
        response = requests.post(url, data=payload)
        result = response.json()
        if response.status_code == 200 and result != -1:
            return {"result": True, "transaction_id": result}
        else:
            return {"result": False, "transaction_id": -1}

    def cancel_payment(self, transaction_id: int) -> dict:
        url = "https://damp-lynna-wsep-1984852e.koyeb.app/"
        payload = {"action_type": "cancel_pay", "transaction_id": transaction_id}
        response = requests.post(url, data=payload)
        result = response.json()
        if response.status_code == 200 and result != -1:
            return {"result": result == 1}
        else:
            return {"result": False}
