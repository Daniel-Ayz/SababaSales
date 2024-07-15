from purchase.interfaces import PaymentServiceInterface
from purchase.models import PaymentMethod
from datetime import datetime
import requests
from django.conf import settings

from ninja.errors import HttpError


class AbstractPaymentService(PaymentServiceInterface):

    ID_LENGTH = 9
    CREDIT_CARD_LENGTH = 16
    SECURITY_CODE_LENGTH = 3
    DATE_LENGTH = 5

    def process_payment(self, payment_details: PaymentMethod) -> dict:
        url = settings.PAYMENT_SERVICE_URL

        expiration_date = payment_details["expiration_date"]
        tuple = expiration_date.split("/")
        if len(tuple) != 2:
            raise HttpError(400, "Invalid Payment Information")
        month, year = tuple

        if (
            payment_details["holder"] == ""
            or len(payment_details["holder_identification_number"]) < self.ID_LENGTH
            or payment_details["currency"] == ""
            or len(payment_details["credit_card_number"]) < self.CREDIT_CARD_LENGTH
            or len(payment_details["expiration_date"]) < self.DATE_LENGTH
            or len(payment_details["security_code"]) < self.SECURITY_CODE_LENGTH
            or payment_details["total_price"] == 0
            or month == ""
            or year == ""
        ):
            raise HttpError(400, "Invalid Payment Information")

        if self.is_expired(payment_details["expiration_date"]):
            raise HttpError(400, "Credit Card is expired")

        year = "20" + year
        handshake_payload = {
            "action_type": "handshake",
        }
        response = requests.post(url, data=handshake_payload, timeout=5)

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

        try:
            response = requests.post(url, data=payload, timeout=5)
            result = response.json()
            if response.status_code == 200 and result != -1:
                return {"result": True, "transaction_id": result}
            else:
                return {"result": False, "transaction_id": -1}
        except requests.exceptions.Timeout:
            return {"result": False, "transaction_id": -1}
        except Exception as e:
            return {"result": False, "transaction_id": -1}

    def cancel_payment(self, transaction_id: int) -> dict:
        url = settings.PAYMENT_SERVICE_URL
        payload = {"action_type": "cancel_pay", "transaction_id": transaction_id}
        response = requests.post(url, data=payload)
        result = response.json()
        if response.status_code == 200 and result != -1:
            return {"result": result == 1}
        else:
            return {"result": False}

    @staticmethod
    def is_expired(date_str):
        # Parse the input string to get month and year
        month, year = map(int, date_str.split("/"))

        # Create a date object for the last day of the given month and year
        expiry_date = datetime(year + 2000, month, 1).replace(
            day=1
        )  # assuming the year is in 2000+ format

        # Get the current date
        current_date = datetime.now()

        # Check if the expiry date has passed
        return expiry_date < current_date
