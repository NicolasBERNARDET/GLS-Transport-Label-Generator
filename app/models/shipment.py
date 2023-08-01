from typing import List


from app.models.consignee import Consignee
from app.models.shipment_unit import ShipmentUnit
from app.models.shipper import Shipper


class Shipment:
    def __init__(self, product: str, consignee: Consignee, shipper: Shipper, shipment_unit: List[ShipmentUnit]) -> None:
        self.Product = product
        self.Consignee = consignee
        self.Shipper = shipper
        self.ShipmentUnit = shipment_unit
