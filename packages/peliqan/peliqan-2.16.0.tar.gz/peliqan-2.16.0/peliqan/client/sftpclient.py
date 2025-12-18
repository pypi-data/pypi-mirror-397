from peliqan.client.base import BaseClient


class SFTPClient(BaseClient):
    def __init__(self, connection, jwt, backend_url):
        super(SFTPClient, self).__init__(jwt, backend_url)
        self.connection = connection

    def sftp_via_proxy(self, path, action, stream=False, **kwargs):
        payload = {
            "connection": self.connection,
            "path": path,
            "action": action,
            "kwargs": kwargs
        }
        url = f"{self.BACKEND_URL}/api/proxy/sftp/"
        return self.call_backend('post', url, stream=stream, json=payload)

    def _write_to_file(self, chunk_iter, encoding, file_object):
        for chunk in chunk_iter:
            chunked_data = chunk
            if encoding:
                chunked_data = chunk.decode(encoding)
            file_object.write(chunked_data)
        return file_object

    def _write_to_memory(self, chunk_iter, encoding):
        chunked_data_array = []
        for chunk in chunk_iter:
            chunked_data = chunk
            if encoding:
                chunked_data = chunk.decode(encoding)

            chunked_data_array.append(chunked_data)

        return {
            'status': 'success',
            'detail': "".join(chunked_data_array) if encoding else b"".join(chunked_data_array)
        }

    def read_file(self, path, encoding='utf-8', file_object=None, *args, **kwargs):
        kwargs = self.args_to_kwargs(args, kwargs)
        chunk_iter = self.sftp_via_proxy(path, 'read_file', stream=True, **kwargs)

        if file_object:
            return self._write_to_file(chunk_iter, encoding, file_object)
        else:
            return self._write_to_memory(chunk_iter, encoding)

    def dir(self, path, *args, **kwargs):
        kwargs = self.args_to_kwargs(args, kwargs)
        response = self.sftp_via_proxy(path, 'dir', **kwargs)
        return response
