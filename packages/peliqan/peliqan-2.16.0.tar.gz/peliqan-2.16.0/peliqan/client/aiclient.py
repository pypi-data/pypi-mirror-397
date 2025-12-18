from openai import OpenAI
from peliqan.client import BaseClient

from peliqan.exceptions import PeliqanClientException


class AIClient(BaseClient):
    def __init__(self, connection, jwt, backend_url):
        super().__init__(jwt, backend_url)
        self.connection = connection

    def _get_open_ai_client(self, data):
        api_key = data.get('password')
        return OpenAI(api_key=api_key)

    def get_ai_connection_data(self):
        url = f"{self.BACKEND_URL}/connection/ai/config/?connection={self.connection}"
        return self.call_backend('get', url)

    def get_client(self):
        data = self.get_ai_connection_data()
        provider = data["connector"]
        if provider == 'openai':
            return self._get_open_ai_client(data)
        else:
            PeliqanClientException("Provider {} is not currently supported.".format(provider))
