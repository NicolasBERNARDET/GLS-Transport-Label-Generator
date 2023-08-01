from marshmallow import Schema, fields


class CredentialsSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
    shipper_id = fields.String(required=True)