import os

import pyodbc

from app.models.credentials import Credentials
from app.queries.gls_auth_query import get_credentials_query
from app.utils.database_config import get_connection_string


def get_gls_credential_async(conn: pyodbc.Connection) -> Credentials | None:
    if os.getenv('MODE') == 'DEBUG':
        username = os.getenv("GLS_USERNAME")
        password = os.getenv("GLS_PASSWORD")
        shipper_id = os.getenv('GLS_SHIPPER_ID')
        if username and password and shipper_id:
            return Credentials(username, password, shipper_id)

    try:
        cursor = conn.cursor()
        cursor.execute(get_credentials_query)
        result = cursor.fetchone()

        if result is not None:
            shipper_id, username, password = result[0], result[1], result[2]
            return Credentials(username, password, shipper_id)

    except pyodbc.Error as e:
        return None


def insert_error_log(server, database, shipment_id: int, error_log: str, number_line: str):
    conn_str = get_connection_string(server, database)
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    query = """INSERT INTO JOURNAL_ERREUR (Commentaire, ContexteNom, ContexteNumLigne, ErrDescription)
                VALUES (?, 'WEB SERVICE GLS', ?, ?)"""
    params = [
        error_log,
        number_line,
        f'ShipmentId : {shipment_id}'
        ]

    try:
        cursor.execute(query, params)
        cursor.commit()
    except Exception as e:
        print(e)
