import requests
from purchase.models import DeliveryMethod
from purchase.interfaces import DeliveryServiceInterface

from ninja.errors import HttpError


class AbstractDeliveryService(DeliveryServiceInterface):
    
    ZIP_LENGTH = 7

    def create_shipment(self, delivery_method: DeliveryMethod) -> dict:
        url = "https://damp-lynna-wsep-1984852e.koyeb.app/"
        if (
            delivery_method["address"] != ""
            and delivery_method["city"] != ""
            and delivery_method["country"] != ""
            and len(delivery_method["zip"]) == self.ZIP_LENGTH
            and delivery_method["name"] != ""
        ):
            
            handshake_payload = {
                "action_type": "handshake",
            }
            response = requests.post(url, data=handshake_payload)
            if response.status_code != 200:
                raise HttpError(400, "Could not connect to payment service")
            
            payload = {
                "action_type": "supply",
                "address": delivery_method["address"],
                "city": delivery_method["city"],
                "country": delivery_method["country"],
                "zip": delivery_method["zip"],
                "name": delivery_method["name"],
            }
        else:
            raise HttpError(400, "Invalid Delivery Information")

        try:
            response = requests.post(url, data=payload)
            result = response.json()

            if response.status_code == 200 and result != -1:
                return {
                    "result": True,
                    "delivery_fee": 0.0,
                    "transaction_id": result,
                }
            else:
                return {"result": False, "delivery_fee": 0.0, "transaction_id": -1}
        except Exception as e:
            return {"result": False, "delivery_fee": 0.0, "transaction_id": -1}

    def cancel_shipment(self, transaction_id: int) -> dict:
        url = "https://damp-lynna-wsep-1984852e.koyeb.app/"
        payload = {"action_type": "cancel_supply", "transaction_id": transaction_id}
        response = requests.post(url, data=payload)
        result = response.json()
        if response.status_code == 200 and result != -1:
            return {"result": result == 1}
        else:
            return {"result": False}
