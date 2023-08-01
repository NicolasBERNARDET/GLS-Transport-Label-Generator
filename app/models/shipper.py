from app.models.address import Address


class Shipper:
    def __init__(self, contact_id: str, alternative_shipper_address: Address | None) -> None:
        self.ContactID = contact_id
        self.AlternativeShipperAddress = alternative_shipper_address
