from purchase.interfaces import DeliveryServiceInterface


class AbstractDeliveryService(DeliveryServiceInterface):
    def create_shipment(self, address: str, package_details: dict, **kwargs) -> dict:
        raise NotImplementedError("The delivery service is not yet implemented.")
