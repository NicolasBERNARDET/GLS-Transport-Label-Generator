from app.models.printing_options import PrintingOptions
from app.models.shipment import Shipment


class ShipmentCreateRequest:
    def __init__(self, shipment: Shipment, printing_options: PrintingOptions) -> None:
        self.Shipment = shipment
        self.PrintingOptions = printing_options
