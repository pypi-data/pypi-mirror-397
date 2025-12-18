from peliqan.client.base import BaseClient
from peliqan.exceptions import PeliqanClientException


class WritebackClient(BaseClient):
    def __init__(self, connection, jwt, backend_url):
        super(WritebackClient, self).__init__(jwt, backend_url)
        self.connection = connection

    def request_endpoint_via_proxy(self, object_name, action, kwargs=None):
        # send to proxy: self.connection, objectName, action, kwargs
        if kwargs is None:
            kwargs = {}

        payload = {
            "connection": self.connection,
            "objectName": object_name,
            "action": action,
            "kwargs": kwargs
        }

        url = f"{self.BACKEND_URL}/api/proxy/"
        result = self.call_backend('post', url, json=payload)
        status = result.get('status')
        if status == 'error':
            _, detail, _ = self._parse_error_response_dict(result)
            result['detail'] = detail

        return result

    def get(self, object_name, *args, **kwargs):
        kwargs = self.args_to_kwargs(args, kwargs)
        response_dict = self.request_endpoint_via_proxy(object_name, 'get', kwargs=kwargs)
        if "detail" in response_dict:
            return response_dict["detail"]
        else:
            return response_dict

    def findone(self, object_name, *args, **kwargs):
        kwargs = self.args_to_kwargs(args, kwargs)
        if "searchterm" not in kwargs:
            raise PeliqanClientException(
                f"Parameter searchterm is required and searchfield is sometimes required for function 'findone'."
            )
        response_dict = self.request_endpoint_via_proxy(object_name, 'findone', kwargs=kwargs)
        if "detail" in response_dict:
            detail = response_dict["detail"]
            if not isinstance(detail, dict):  # replace empty string response "" (if no record found) with {}
                detail = {}
            return detail
        else:
            return response_dict

    def list(self, object_name, **kwargs):
        response_dict = self.request_endpoint_via_proxy(object_name, 'list', kwargs=kwargs)
        return response_dict

    def add(self, object_name, *args, **kwargs):
        # allow using both keyword arguments or a dict as argument:
        # pq.add("contact", name='John', city='NY') or pq.add("contact", contact_obj)
        kwargs = self.args_to_kwargs(args, kwargs)
        response_dict = self.request_endpoint_via_proxy(object_name, 'add', kwargs=kwargs)
        return response_dict

    def update(self, object_name, *args, **kwargs):
        # allow using both keyword arguments or a dict as argument:
        # pq.update("contact", name='John', city='NY') or pq.update("contact", contact_obj)
        kwargs = self.args_to_kwargs(args, kwargs)
        response_dict = self.request_endpoint_via_proxy(object_name, 'update', kwargs=kwargs)
        return response_dict

    def upsert(self, object_name, *args, **kwargs):
        # allow using both keyword arguments or a dict as argument:
        # pq.update("contact", name='John', city='NY') or pq.update("contact", contact_obj)
        kwargs = self.args_to_kwargs(args, kwargs)
        if "searchterm" not in kwargs:
            raise PeliqanClientException(
                f"Parameter searchterm is required and searchfield is sometimes required for function 'upsert'.")
        if "searchfield" not in kwargs:
            kwargs["searchfield"] = None
        response_dict_findone = self.request_endpoint_via_proxy(object_name, 'findone', kwargs=kwargs)
        kwargs.pop('searchfield', None)
        kwargs.pop('searchterm', None)
        if "detail" in response_dict_findone and "id" in response_dict_findone["detail"]:
            kwargs["id"] = response_dict_findone["detail"]["id"]
            response_dict = self.request_endpoint_via_proxy(object_name, 'update', kwargs=kwargs)
        else:
            response_dict = self.request_endpoint_via_proxy(object_name, 'add', kwargs=kwargs)
        return response_dict

    def delete(self, object_name, *args, **kwargs):
        kwargs = self.args_to_kwargs(args, kwargs)
        response_dict = self.request_endpoint_via_proxy(object_name, 'delete', kwargs=kwargs)
        return response_dict

    def copy(self, object_name, **kwargs):
        response_dict = self.request_endpoint_via_proxy(object_name, 'copy', kwargs=kwargs)
        return response_dict

    def rename(self, object_name, **kwargs):
        response_dict = self.request_endpoint_via_proxy(object_name, 'rename', kwargs=kwargs)
        return response_dict

    def apicall(self, path, method="get", body=None, **kwargs):
        kwargs["path"] = path
        kwargs["method"] = method
        kwargs["body"] = body
        response_dict = self.request_endpoint_via_proxy("", 'apicall', kwargs=kwargs)
        return response_dict
