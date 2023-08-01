import asyncio
import base64
import json
import os
import re
import traceback
from dataclasses import asdict
from http import HTTPStatus
from json import JSONEncoder
from typing import Any, List, Tuple

import httpx as httpx
import pyodbc
import requests
from _decimal import Decimal

from app.blueprints.schemas.credentials_schema import CredentialsSchema
from app.http.requests.shipment_create_request import ShipmentCreateRequest
from app.http.requests.shipment_request import ShipmentRequest
from app.http.responses.shipment_create_response import ShipmentCreateResponse
from app.http.responses.shipment_response import ShipmentResponse
from app.http.security.authorization import Authorization
from app.models.address import Address
from app.models.consignee import Consignee
from app.models.credentials import Credentials
from app.models.printing_options import PrintingOptions
from app.models.return_labels import ReturnLabels
from app.models.shipment import Shipment
from app.models.shipment_unit import ShipmentUnit
from app.models.shipper import Shipper
from app.proxy.file_central_proxy import FileCentralProxy
from app.queries import gls_auth_query
from app.queries.shipment_queries import shipment_info_query
from app.utils.database import get_gls_credential_async, insert_error_log
from app.utils.database_config import get_connection_string
from app.utils.encoders import json_encoder_default
from app.utils.output_format import OutputFormat


class ShipmentController:

    def __init__(self, shipment_request: ShipmentRequest):
        self.request_data = shipment_request

    async def create_shipment_async(self) -> ShipmentResponse:

        conn_str = get_connection_string(self.request_data.server, self.request_data.database)

        try:
            async with httpx.AsyncClient() as client:
                conn = await self.create_connection_async(conn_str)
                cursor = conn.cursor()

                query = shipment_info_query
                params = [self.request_data.shipment_id]

                cursor.execute(query, params)
                result = cursor.fetchone()

                if result is None:
                    return ShipmentResponse('Shipment not found in database', HTTPStatus.BAD_REQUEST)

                street, street_number = self.extract_street_details(result.ADDRESS2)

                credentials = get_gls_credential_async(conn)

                if credentials.__isvalid__() is not True:
                    return ShipmentResponse('No GLS account found in database', HTTPStatus.UNAUTHORIZED)

                printing_options, shipment = self.create_shipment(result, street, street_number,
                                                                  self.request_data.output_format_value,
                                                                  credentials)
                shipment_create_request = ShipmentCreateRequest(shipment, printing_options)
                json_data = json.dumps(shipment_create_request, default=json_encoder_default)

                response = await self.send_to_gls_async(json_data, credentials, client)
                if isinstance(response, ShipmentCreateResponse):
                    self.save_label(response)
                    return ShipmentResponse(f'Label {response.track_id} successfully created', HTTPStatus.OK)
                else:
                    status, data = response
                    return ShipmentResponse(data, status)
        except pyodbc.Error as e:
            insert_error_log(self.request_data.server, self.request_data.database, self.request_data.shipment_id,
                             str(e),
                             str(traceback.extract_stack()[-1][1]))
            return ShipmentResponse(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)
        except Exception as e:
            insert_error_log(self.request_data.server, self.request_data.database, self.request_data.shipment_id,
                             str(e),
                             str(traceback.extract_stack()[-1][1]))
            return ShipmentResponse(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)

    @staticmethod
    def extract_street_details(address: str):
        matches = re.findall(r'^(\d+)\s*(.*)$', address)
        street_number = ''
        street = address
        if matches:
            street_number, street = matches[0]
        return street, street_number

    @staticmethod
    async def create_connection_async(conn_str):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: pyodbc.connect(conn_str))

    @staticmethod
    def create_shipment(result, street, street_number, output_format: OutputFormat, credentials: Credentials):
        consignee_address = Address(
            result.NAME1,
            result.ADDRESS2,
            result.ADDRESS3,
            result.COUNTRYCODE,
            result.ZIPCODE,
            result.CITY,
            street,
            street_number,
            result.EMAIL,
            result.NAME1,
            result.MOBILEPHONE,
            result.PHONE
        )
        result.WEIGHT = 1
        consignee = Consignee(123, consignee_address)
        shipper = Shipper(credentials.shipper_id, None)
        shipment_unit: List[ShipmentUnit] = [ShipmentUnit(result.WEIGHT)]

        # default return is PDF
        return_label = ReturnLabels("NONE", "PDF")

        if output_format == OutputFormat.PDF:
            return_label = ReturnLabels("NONE", "PDF")
        elif output_format == OutputFormat.ZPL:
            return_label = ReturnLabels("ZPL_200", "ZEBRA")

        printing_options = PrintingOptions(return_label)
        shipment = Shipment('PARCEL', consignee, shipper, shipment_unit)
        return printing_options, shipment

    @staticmethod
    async def send_to_gls_async(json_data: str, credentials: Credentials, client: httpx.AsyncClient):
        url = os.getenv('URL')
        headers = {
            'Content-Type': 'application/glsVersion1+json',
            'Accept': 'application/glsVersion1+json, application/json',
            'Authorization': Authorization.get_basic_auth_header(credentials.username, credentials.password)
        }
        response = await client.post(f'{url}/shipments', data=json_data, headers=headers)

        if response.status_code == 200:
            return_values = response.text
            json_response = json.loads(return_values)
            pdf = json_response['CreatedShipment']['PrintData'][0]['Data']
            filename = json_response['CreatedShipment']['ParcelData'][0]['TrackID']
            return ShipmentCreateResponse(pdf, filename)

        elif response.status_code == HTTPStatus.UNAUTHORIZED:
            return response.status_code, 'Invalid credentials'
        else:
            response_headers = response.headers
            if 'message' in response_headers:
                return response.status_code, response_headers['message']
            return response.status_code, 'Unknown error'

    def save_label(self, shipment_create_response: ShipmentCreateResponse) -> bool:
        try:
            file_central_path = FileCentralProxy.get_file_central(self.request_data.server)
            data = base64.b64decode(shipment_create_response.data)

            if self.request_data.output_format_value == OutputFormat.PDF:
                file_extension = ".pdf"
            else:
                file_extension = ".txt"

            with open(
                    '{}{}\\{}{}'.format(
                        file_central_path,
                        self.request_data.saving_file_path,
                        shipment_create_response.track_id,
                        file_extension
                    ),
                    "wb"
            ) as f:
                f.write(data)
            return True
        except Exception as e:
            raise

    @staticmethod
    def get_gls_credential(conn: pyodbc.Connection) -> Tuple[str, str] | None:
        try:
            cursor = conn.cursor()
            cursor.execute(gls_auth_query.get_credentials_query)
            result = cursor.fetchone()

            if result is not None:
                username, password = result[0], result[1]
                return username, password

        except pyodbc.Error:
            return None
