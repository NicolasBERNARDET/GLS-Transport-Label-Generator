from http import HTTPStatus


class ShipmentResponse:
    def __init__(self, data:str, status_code: HTTPStatus):
        self.data = data
        self.status_code = status_code
