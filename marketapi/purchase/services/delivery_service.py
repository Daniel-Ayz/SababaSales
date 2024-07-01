import requests
from purchase.models import DeliveryMethod
from purchase.interfaces import DeliveryServiceInterface


class AbstractDeliveryService(DeliveryServiceInterface):
    def create_shipment(self, delivery_method: DeliveryMethod) -> dict:
        url = "https://damp-lynna-wsep-1984852e.koyeb.app/"

        if (
            delivery_method.address != ""
            and delivery_method.city != ""
            and delivery_method.country != ""
            and delivery_method.zip != ""
            and delivery_method.name != ""
        ):
            payload = {
                "action_type": "supply",
                "address": delivery_method.address,
                "city": delivery_method.city,
                "country": delivery_method.country,
                "zip": delivery_method.zip,
                "name": delivery_method.name,
            }
        else:
            raise ValueError("Delivery information is missing")

        response = requests.post(url, data=payload)
        if response.status_code == 200:
            result = response.json()
            return {
                "result": True,
                "delivery_fee": 0.0,
                "transaction_id": result.get("transaction_id", -1),
            }
        else:
            return {"result": False, "delivery_fee": 0.0, "transaction_id": -1}

    def cancel_shipment(self, transaction_id: int) -> dict:
        url = "https://damp-lynna-wsep-1984852e.koyeb.app/"
        payload = {"action_type": "cancel_supply", "transaction_id": transaction_id}
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            result = response.json()
            return {"result": result.get("result", -1) == 1}
        else:
            return {"result": False}
