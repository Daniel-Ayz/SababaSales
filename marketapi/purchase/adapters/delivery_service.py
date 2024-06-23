import requests

from purchase.interfaces import DeliveryServiceInterface


class AbstractDeliveryService(DeliveryServiceInterface):
    def create_shipment(self, address: str, item_quantity: float, **kwargs) -> dict:
        url = "https://damp-lynna-wsep-1984852e.koyeb.app/"
        payload = {
            "action_type": "supply",
            "name": kwargs.get("name", "Default Name"),
            "address": address,
            "city": kwargs.get("city", "Default City"),
            "country": kwargs.get("country", "Default Country"),
            "zip": kwargs.get("zip", "0000000"),
        }
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
