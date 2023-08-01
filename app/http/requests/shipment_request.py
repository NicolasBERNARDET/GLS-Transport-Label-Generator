class ShipmentRequest:
    def __init__(self, data):
        self.server = data.get('server')
        self.database = data.get('database')
        self.shipment_id = data.get('shipment_id')
        self.saving_file_path = data.get('saving_file_path')
        self.output_format_value = data.get('output_format')
