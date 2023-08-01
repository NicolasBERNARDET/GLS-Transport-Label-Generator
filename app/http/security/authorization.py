import base64


class Authorization:
    @staticmethod
    def get_basic_auth_header(username: str, password: str):
        credentials = f'{username}:{password}'

        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        return f'Basic {encoded_credentials}'
