import ast
import json

import requests

from peliqan.exceptions import PeliqanClientException
from peliqan.utils import _serialize_data


class BaseClient:

    def __init__(self, jwt, backend_url):
        self.JWT = jwt
        self.BACKEND_URL = backend_url

    def get_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": "JWT %s" % self.JWT
        }

    def _get_stream_iter(self, response):
        try:
            for chunk in response.iter_content(chunk_size=32768):
                yield chunk
        except Exception as e:
            raise PeliqanClientException(f"Error while streaming data. Original error is {e}")

    def _parse_error_response_dict(self, response_dict):
        if not isinstance(response_dict, dict):
            return None, None, response_dict

        error_code = response_dict.get("error")
        details = response_dict.get('detail', '')

        try:
            if not isinstance(details, dict):
                details = ast.literal_eval(details)

                if isinstance(details, tuple):
                    error = details[0]
                    trace_id = details[1]
                    details = {'trace_id': trace_id.strip('TraceId: '), **error}
        except Exception:
            return error_code, None, details

        parsed_response = []
        error_type = details.get('type')
        if error_type:
            parsed_response.append(error_type)

        operation = details.get('operation')
        if operation:
            parsed_response.append(f"during {operation}:")

        message = details.get('message')
        if message:
            parsed_response.append(message)

        message = details.get('description')
        if message:
            parsed_response.append(message)

        stack_trace = details.get('stack_trace')
        if stack_trace:
            line_details = stack_trace[-1]
            parsed_response.append(f"\nin {line_details}")

        if not parsed_response:
            str_data = json.dumps(details)
            parsed_response.append(str_data)

        return error_code, details, ' '.join(parsed_response)

    def call_backend(self, method, url, expected_status_code=200, **kwargs):
        if not kwargs.get('headers'):
            headers = self.get_headers()
            kwargs.update(headers=headers)

        json_data = kwargs.get('json')
        if json_data:
            serialized_data = _serialize_data(json_data)
            kwargs['json'] = serialized_data

        stream = kwargs.get('stream', False)
        response = requests.request(method, url, **kwargs)

        if stream:
            return self._get_stream_iter(response)
        else:
            try:
                response_dict = response.json()
            except ValueError:
                response_dict = {}

        # handle error responses
        if response.status_code != expected_status_code:
            error_message = f"Server responded with status code {response.status_code}. "
            error_code = None
            if not response_dict:
                response_dict = response.text

            error_dict = None
            if response_dict:
                error_code, error_dict, parsed_error_response = self._parse_error_response_dict(response_dict)
                error_message += f"{parsed_error_response}"

            raise PeliqanClientException(error_message, error_code, error_dict)

        return response_dict

    def args_to_kwargs(self, args, kwargs):
        """
        Used to allow using both a dict argument or keyword arguments:
        pq.add("contact", name='John', city='NY') or
        pq.add("contact", contact_obj)
        """
        for arg in args:
            if type(arg) != dict:
                raise PeliqanClientException("Only arguments of type dict and kwargs are accepted")
            kwargs.update(**arg)
        return kwargs
