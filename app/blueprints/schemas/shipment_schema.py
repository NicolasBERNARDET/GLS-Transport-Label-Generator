from marshmallow import Schema, fields, ValidationError, validates, validate


class ShipmentSchema(Schema):
    server = fields.String(required=True)
    database = fields.String(required=True)
    shipment_id = fields.Integer(required=True)
    saving_file_path = fields.String(required=True)
    output_format = fields.String(required=True, alidate=validate.OneOf(['PDF', 'ZPL']))

    @validates('shipment_id')
    def validate_shipment_id(self, value):
        if value <= 0:
            raise ValidationError("shipment_id must be an positive integer")