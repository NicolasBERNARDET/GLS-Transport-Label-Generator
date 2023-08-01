class Credentials:
    def __init__(self, username: str, password: str, shipper_id: str):
        self.username = username
        self.password = password
        self.shipper_id = shipper_id

    def __isvalid__(self):
        return len(self.username) > 0 and len(self.password) > 0 and len(self.shipper_id) > 0
