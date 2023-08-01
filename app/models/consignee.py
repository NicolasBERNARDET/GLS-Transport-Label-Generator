from app.models.address import Address


class Consignee:
    def __init__(self, consignee_id: int | None, address: Address):
        self.ConsigneeID = consignee_id
        self.Address = address
