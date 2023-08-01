import asyncio
import json
from http import HTTPStatus

from flask import Blueprint, request

from app.blueprints.schemas.logics import required_params
from app.blueprints.schemas.shipment_schema import ShipmentSchema
from app.controllers.shipment_controller import ShipmentController
from app.http.requests.shipment_request import ShipmentRequest
from app.utils.database import insert_error_log
from app.utils.output_format import OutputFormat

shipments_blueprint = Blueprint('shipments', __name__)


@shipments_blueprint.route('/create-label', methods=['POST'])
@required_params(ShipmentSchema())
def create_label():
    data = request.get_json()
    request_data = ShipmentRequest(data)

    try:
        request_data.output_format_value = OutputFormat(request_data.output_format_value)
    except ValueError:
        return json.dumps({"error": "Invalid output_format"}), HTTPStatus.BAD_REQUEST

    shipment_controller = ShipmentController(request_data)
    response = asyncio.run(shipment_controller.create_shipment_async())

    if response.status_code != HTTPStatus.OK:
        insert_error_log(request_data.server, request_data.database, request_data.shipment_id, response.data, str(0))
        return json.dumps({"error": response.data}), response.status_code
    return json.dumps({'message': response.data}), response.status_code
