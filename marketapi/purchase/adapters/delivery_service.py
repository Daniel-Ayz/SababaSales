from purchase.interfaces import DeliveryServiceInterface


class AbstractDeliveryService(DeliveryServiceInterface):
    def create_shipment(
        self, address: str, package_details: dict, flag, **kwargs
    ) -> dict:
        return {"result": flag, "delivery_fee": 0.0}
