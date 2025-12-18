from peliqan.exceptions import PeliqanClientException
from peliqan.client import BaseClient

from peliqan.utils import empty, _retry_get_resource_status


class BackendServiceClient(BaseClient):
    def __init__(self, jwt, backend_url):
        super(BackendServiceClient, self).__init__(jwt, backend_url)
        self._cache = {
            'connection': {},
            'database': {},
            'schema': {},
            'table': {},
            'interface': {}
        }

    def get_cached_results(self, resource_type, resource_id_or_name, property_name):
        try:
            resource_id_or_name = resource_id_or_name.lower()
        except AttributeError:
            pass

        resource_type = resource_type.lower()
        property_name = property_name.lower()
        return self._cache.get(resource_type, {}).get(resource_id_or_name, {}).get(property_name)

    def _cache_connection_data(self, data):
        connection_name = data.get('connection_name', '')
        if connection_name:
            connection_name = connection_name.lower()
            connection_id = data['connection_id']
            if connection_id:
                data_to_cache = {
                    connection_id: {
                        'connection_name': connection_name
                    },
                    connection_name: {
                        'connection_id': connection_id
                    }
                }
                self._cache['connection'].update(data_to_cache)

    def _cache_database_data(self, data):
        database_name = data.get('database_name', '')
        if database_name:
            database_name = database_name.lower()
            database_id = data['database_id']
            if database_id:
                data_to_cache = {
                    database_id: {
                        'database_name': database_name
                    },
                    database_name: {
                        'database_id': database_id
                    }
                }
                self._cache['database'].update(data_to_cache)

    def _cache_schema_data(self, data):
        schema_name = data.get('schema_name', '')
        if schema_name:
            schema_id = data['schema_id']
            if schema_id:
                data_to_cache = {
                    schema_id: {
                        'schema_name': schema_name
                    },
                    schema_name: {
                        'schema_id': schema_id
                    }
                }
                self._cache['schema'].update(data_to_cache)

    def _cache_table_and_field_data(self, data):
        table_name = data.get('table_name', '')
        if table_name:
            table_id = data['table_id']
            if table_id:
                data_to_cache = {
                    table_name: {
                        'table_id': table_id,
                    },
                    table_id: {
                        'table_name': table_name
                    }
                }
                self._cache['table'].update(data_to_cache)

                # cache field
                field_name = data.get('field_name', '')
                if field_name:
                    field_physical_name = data['field_physical_name']
                    if field_physical_name:
                        data_to_cache[table_name].update({field_name: field_physical_name})
                        data_to_cache[table_id].update({field_name: field_physical_name})

    def _cache_interface_data(self, data):
        interface_name = data.get('interface_name', '')
        if interface_name:
            interface_id = data['interface_id']
            data_to_cache = {
                interface_name: {
                    'interface_id': interface_id,
                },
                interface_id: {
                    'interface_name': interface_name
                }
            }
            self._cache['interface'].update(data_to_cache)

    def _get_default_dw_info(self):
        url = f"{self.BACKEND_URL}/api/applications/default_dw_info/"
        return self.call_backend("get", url)

    def _update_cache(self, data):
        self._cache_connection_data(data)
        self._cache_database_data(data)
        self._cache_schema_data(data)
        self._cache_table_and_field_data(data)
        self._cache_interface_data(data)

    def find_connection(self, connection_id=None, connection_name=None):
        """

        :param connection_id:
        :param connection_name:
        :return:
        """
        url = f"{self.BACKEND_URL}/api/database/resource/lookup/connection/"
        data = {
            'connection_id': connection_id,
            'connection_name': connection_name,
        }
        data = self.call_backend("get", url, json=data)

        self._update_cache(data)
        return data

    def find_database(self, connection_id=None, connection_name=None, database_id=None, database_name=None):
        """

        :param connection_id:
        :param connection_name:
        :param database_id:
        :param database_name:
        :return:
        """
        url = f"{self.BACKEND_URL}/api/database/resource/lookup/database/"
        data = {
            'connection_id': connection_id,
            'connection_name': connection_name,
            'database_id': database_id,
            'database_name': database_name,
        }
        data = self.call_backend("get", url, json=data)

        self._update_cache(data)
        return data

    def find_schema(self, connection_id=None, connection_name=None, database_id=None, database_name=None,
                    schema_id=None, schema_name=None):
        """

        :param connection_id:
        :param connection_name:
        :param database_id:
        :param database_name:
        :param schema_id:
        :param schema_name:
        :return:
        """
        url = f"{self.BACKEND_URL}/api/database/resource/lookup/schema/"
        data = {
            'connection_id': connection_id,
            'connection_name': connection_name,
            'database_id': database_id,
            'database_name': database_name,
            'schema_id': schema_id,
            'schema_name': schema_name,
        }
        data = self.call_backend("get", url, json=data)

        self._update_cache(data)
        return data

    def find_table_or_field(
        self, connection_id=None, connection_name=None, database_id=None, database_name=None,
        schema_id=None, schema_name=None, table_id=None, table_name=None,
        field_id=None, field_name=None
    ):
        """
        Find the table information by passing in a table_id or table_name.
        Optionally pass in a field_id or field_name to retrieve that fields info.

        We can also pass in the optional connection_id/connection_name and optional database_id/database_name
        if we want to restrict the search.

        :param connection_id: (Optional) id of the connection the table belongs to.
        :param connection_name: (Optional) name of the connection the table belongs to.
        :param database_id: (Optional) name of the database the table belongs to.
        :param database_name: (Optional) name of the database the table belongs to.
        :param schema_id: (Optional) id of the schema the table belongs to.
        :param schema_name: (Optional) name of the schema the table belongs to.
        :param table_id: id of the table to find.
        :param table_name: name of the table to find.
        :param field_id: (Optional) id of the field to find.
        :param field_name: (Optional) name of the field to find.
        :return:
        """
        url = f"{self.BACKEND_URL}/api/database/resource/lookup/table/"
        data = {
            'connection_id': connection_id,
            'connection_name': connection_name,
            'database_id': database_id,
            'database_name': database_name,
            'schema_id': schema_id,
            'schema_name': schema_name,
            'table_id': table_id,
            'table_name': table_name,
            'field_id': field_id,
            'field_name': field_name
        }
        data = self.call_backend("get", url, json=data)

        self._update_cache(data)
        return data

    def find_interface(self, interface_id=None, interface_name=None):
        url = f"{self.BACKEND_URL}/api/resource/lookup/interface/"
        data = {
            'interface_id': interface_id,
            'interface_name': interface_name
        }
        data = self.call_backend("get", url, json=data)

        self._update_cache(data)
        return data
    def hide_table(self, table_id, schema_name=None, database_name=None, connection_name=None):
        url = f"{self.BACKEND_URL}/api/database/tables/{table_id}/hide/"
        data ={
            'schema_name': schema_name,
            'database_name': database_name,
            'connection_name': connection_name
        }
        data = self.call_backend("post", url, json=data)
        return data

    def find_resource(self, resource_type, resource_id=None, resource_name=None, **kwargs):

        if resource_type not in ('connection', 'database', 'schema', 'table', 'interface'):
            raise PeliqanClientException(
                f"{resource_type} is not valid. "
                "Allowed resource types are "
                "'connection', 'database', 'schema', 'table', 'interface'."
            )

        if not resource_id and not resource_name:
            raise PeliqanClientException("resource_id or resource_name must be provided as kwargs.")

        if resource_type.lower() == 'connection':
            data = {
                'connection_id': resource_id,
                'connection_name': resource_name
            }
            # find connection
            return self.find_connection(**data)

        elif resource_type.lower() == 'database':
            data = {
                'database_id': resource_id,
                'database_name': resource_name,
            }
            # find database
            return self.find_database(**data, **kwargs)

        elif resource_type.lower() == 'schema':
            data = {
                'schema_id': resource_id,
                'schema_name': resource_name
            }
            return self.find_schema(**data, **kwargs)

        elif resource_type.lower() == 'table':
            data = {
                'table_id': resource_id,
                'table_name': resource_name
            }
            return self.find_table_or_field(**data, **kwargs)

        elif resource_type.lower() == 'interface':
            data = {
                'interface_id': resource_id,
                'interface_name': resource_name
            }
            return self.find_interface(**data)

        else:
            raise PeliqanClientException(f"{resource_type} is not valid. "
                                         f"Allowed resource types are 'connection', 'database', 'schema', 'table'.")

    def _is_refresh_allowed(self, resource_type):
        if resource_type not in ['connection', 'database', 'schema', 'table']:
            raise PeliqanClientException(f"{resource_type} is not valid. "
                                         f"Allowed resource types are 'connection', 'database', 'schema', 'table'.")

    def _get_resource_id(self, resource_id, resource_name, resource_type, **kwargs):
        if not resource_id and not resource_name:
            raise PeliqanClientException(f"{resource_type}_id or {resource_type}_name must be provided.")

        elif not resource_id and resource_name:
            resource_id = self.get_cached_results(resource_type, resource_name, f'{resource_type}_id')

        if not resource_id:
            lookup_data = self.find_resource(resource_type=resource_type, resource_name=resource_name, **kwargs)
            resource_id = lookup_data[f'{resource_type}_id']

        return resource_id

    def refresh_resource(self, resource_type, refresh_baseurl, resource_name=None, resource_id=None, **kwargs):
        self._is_refresh_allowed(resource_type)
        data= {}
        if (resource_type == 'table'):
            data = {
                'resource_id': resource_id,
                'resource_name': resource_name,
                'resource_type': resource_type,
                **kwargs
            }
            url = f"{self.BACKEND_URL}/api/database/tables/refresh_table/"
        else :
            resource_id = self._get_resource_id(resource_id, resource_name, resource_type, **kwargs)
            url = refresh_baseurl % resource_id
        # call sync url
        response = self.call_backend("get", url, expected_status_code=200,json=data)
        prepared_response = {
            'task_id': response['task_id'],
            'run_data': response.get('run_data'),
            'detail': response['detail'],
            'syncing': response['syncing']
        }
        return prepared_response

    def recreate_pipeline(self, resource_id, resource_name, **kwargs):
        resource_id = self._get_resource_id(resource_id, resource_name, 'connection', **kwargs)
        url = f"{self.BACKEND_URL}/api/servers/%s/resync/" % resource_id
        response = self.call_backend("get", url, json=kwargs)
        return response

    def update_connector_file(self, resource_id, resource_name, **kwargs):
        resource_id = self._get_resource_id(resource_id, resource_name, 'connection', **kwargs)
        url = f"{self.BACKEND_URL}/api/servers/%s/pipeline/connector/" % resource_id
        response = self.call_backend("post", url, json=kwargs)
        return response

    def get_refresh_resource_task_status(
        self,
        resource_type, refresh_baseurl,
        resource_name=None, resource_id=None,
        task_id='', **kwargs
    ):
        self._is_refresh_allowed(resource_type)
        resource_id = self._get_resource_id(resource_id, resource_name, resource_type, **kwargs)
        url = refresh_baseurl % resource_id + f"?task_id={task_id}"

        # call sync task status url
        return self.call_backend('get', url, expected_status_code=200)

    def get_refresh_connection_task_status(
        self,
        connection_name=None,
        connection_id=None,
        task_id=None,
        pipeline_run_id=None,
        timeout=None,
        **kwargs
    ):
        resource_id = self._get_resource_id(
            resource_id=connection_id,
            resource_name=connection_name,
            resource_type='connection',
            **kwargs
        )

        url = f"{self.BACKEND_URL}/api/servers/{resource_id}/syncdb/status/?"

        if task_id:
            url += f"task_id={task_id}&"

        if pipeline_run_id:
            url += f"pipeline_run_id={pipeline_run_id}&"

        if timeout:
            url += f"timeout={timeout}"

        # call sync task status url
        return self.call_backend('get', url, expected_status_code=200)

    def get_recreate_pipeline_status(
        self,
        connection_name=None,
        connection_id=None,
        task_id=None,
        timeout=None,
        **kwargs
    ):
        resource_id = self._get_resource_id(
            resource_id=connection_id,
            resource_name=connection_name,
            resource_type='connection',
            **kwargs
        )

        url = f"{self.BACKEND_URL}/api/servers/{resource_id}/resync/status/?"

        if task_id:
            url += f"task_id={task_id}&"

        if timeout:
            url += f"timeout={timeout}"

        # call sync task status url
        return self.call_backend('get', url, expected_status_code=200)

    def update_record(self, url, data):
        return self.call_backend("patch", url, json=data, expected_status_code=204)

    def get_cdclogs(self, table_id, writeback_status, change_type, latest_changes_first=False):
        url = f"{self.BACKEND_URL}/api/database/cdclogs/table/{table_id}/?latest_changes_first={latest_changes_first}"

        if writeback_status or change_type:
            url += "&"
            if writeback_status:
                url += f"writeback_status={writeback_status}&"

            if change_type:
                url += f"change_type={change_type}"

        response_dict = self.call_backend("get", url)
        return response_dict

    def update_writeback_status(self, table_id, change_id, writeback_status):
        url = f"{self.BACKEND_URL}/api/database/cdclogs/table/{table_id}/changes/{change_id}/writeback_status/"

        data = {
            "change_id": change_id,
            "writeback_status": writeback_status
        }

        response_dict = self.call_backend("patch", url, json=data)
        return response_dict

    def list_servers(self):
        url = f"{self.BACKEND_URL}/api/servers/"
        response_dict = self.call_backend("get", url)
        return response_dict

    def list_databases(self):
        url = f"{self.BACKEND_URL}/api/applications/"
        response_dict = self.call_backend("get", url)
        return response_dict

    def get_table(self, table_id):
        url = f"{self.BACKEND_URL}/api/database/tables/{table_id}/"
        response_dict = self.call_backend("get", url)
        return response_dict

    def create_query(
        self,
        table_name,
        query,
        database_id=None,
        schema_id=None,
    ):
        url = f"{self.BACKEND_URL}/api/database/tables/create-sql-query/"
        if schema_id and not database_id:
            response = self.get_schema(schema_id)
            database_id = response['database']

        if database_id:
            url = f"{self.BACKEND_URL}/api/database/tables/database/{database_id}/"

        data = {
            'table_type': 'query',
            'schema_id': schema_id,
            'name': table_name,
            'query': query,
        }

        response_dict = self.call_backend("post", url, json=data)

        return response_dict

    def get_final_query(self, table_id=None):
        url = f"{self.BACKEND_URL}/api/database/tables/final-query/"

        if table_id:
            url_params = f"?table_id={table_id}"
        else:
            raise PeliqanClientException("table_id or custom_query and custom_query_dialect must be provided.")

        url += url_params

        response_dict = self.call_backend("get", url)
        final_query = response_dict.get('final_query', '')
        return final_query

    def update_table(
        self,
        table_id,
        name=None,
        query=None,
        settings=None,
        run_on_peliqan_trino=empty,
        materialize=empty,
        is_view=empty,
        replicate=empty,
        replicate_settings=empty
    ):
        url = f"{self.BACKEND_URL}/api/database/tables/%s/" % table_id
        data = {}

        if name:
            data['name'] = name

        if query:
            data['query'] = query

        if run_on_peliqan_trino != empty:
            data['run_on_peliqan_trino'] = run_on_peliqan_trino

        if is_view != empty:
            data['is_view'] = is_view

        if not settings:
            settings = {}

        if materialize != empty:
            settings['materialize_settings'] = {
                'materialize': materialize
            }
        if replicate != empty:
            if replicate_settings == empty:
                replicate_settings = {}
            settings['replicate_settings'] = {
                "replicate": replicate,
                **replicate_settings
            }

        if settings:
            data['settings'] = settings

        response_dict = self.call_backend("patch", url, json=data)
        return response_dict

    def update_database_metadata(self, database_id, description=None, tags=None):
        url = f"{self.BACKEND_URL}/api/applications/%s/data-catalog/" % database_id
        data = {}
        if description:
            data["description"] = description
        if tags:
            data["tags"] = tags
        response_dict = self.call_backend("patch", url, json=data)
        return response_dict

    def get_schema(self, schema_id):
        url = f"{self.BACKEND_URL}/api/database/schemas/%s/" % schema_id
        response_dict = self.call_backend("get", url)
        return response_dict

    def update_schema(self, schema_id, name):
        url = f"{self.BACKEND_URL}/api/database/schemas/%s/" % schema_id
        data = {}
        if name:
            data["schema_name"] = name
        response_dict = self.call_backend("patch", url, json=data)
        return response_dict

    def delete_schema(self, schema_id):
        url = f"{self.BACKEND_URL}/api/database/schemas/%s/" % schema_id
        return self.call_backend("delete", url)

    def update_table_metadata(
        self,
        table_id,
        description=None,
        lineage_annotation=None,
        tags=None,
        primary_field_id=None
    ):
        url = f"{self.BACKEND_URL}/api/database/tables/%s/details/" % table_id
        data = {}
        if description:
            data["description"] = description

        if lineage_annotation:
            data['lineage_annotation'] = lineage_annotation

        if tags:
            data["tags"] = tags

        if primary_field_id:
            data["primary_field_id"] = primary_field_id
        response_dict = self.call_backend("patch", url, json=data)
        return response_dict

    def update_field_metadata(self, field_id, description=None, tags=None):
        url = f"{self.BACKEND_URL}/api/database/fields/%s/data-catalog/" % field_id
        data = {}
        if description:
            data["description"] = description
        if tags:
            data["tags"] = tags
        response_dict = self.call_backend("patch", url, json=data)
        return response_dict

    def list_interfaces(self):
        url = f"{self.BACKEND_URL}/api/interfaces/"
        response_dict = self.call_backend("get", url)
        return response_dict

    def get_interface(self, interface_id):
        url = f"{self.BACKEND_URL}/api/interfaces/{interface_id}/"
        return self.call_backend("get", url)

    def update_interface(
        self,
        interface_id,
        **kwargs
    ):
        url = f"{self.BACKEND_URL}/api/interfaces/{interface_id}/"

        data = {k: v for k, v in kwargs.items() if v is not empty}
        return self.call_backend("patch", url, json=data)

    def get_groups(self):
        url = f"{self.BACKEND_URL}/api/groups/"
        return self.call_backend("get", url)

    def create_interface(self, group_id, group_name, **kwargs):
        data = {k: v for k, v in kwargs.items() if v is not None}
        if not group_id:
            groups = self.get_groups()
            if groups:
                if group_name:
                    group_id = next((g['id'] for g in groups if g['name'] == group_name), None)
                else:
                    group_id = groups[0]['id']
            else:
                raise PeliqanClientException("No groups found. Please create a group first.")

        url = f"{self.BACKEND_URL}/api/interfaces/group/{group_id}/"

        return self.call_backend("post", url, json=data)

    def get_interface_state(self, interface_id):
        url = f"{self.BACKEND_URL}/api/interfaces/{interface_id}/state/"
        response = self.call_backend("get", url)
        return response.get('state', '')

    def set_interface_state(self, interface_id, state):
        url = f"{self.BACKEND_URL}/api/interfaces/{interface_id}/state/"
        data = {'state': state}
        return self.call_backend("post", url, json=data)

    def get_pipeline_logs(self, pipeline_run_id):
        if not pipeline_run_id:
            raise PeliqanClientException("'pipeline_run_id' must be provided")

        url = f"{self.BACKEND_URL}/api/pipeline_runs/{pipeline_run_id}/logs/"
        return self.call_backend("get", url)

    def get_pipeline_runs(self, connection_id=None, run_id=None, page=1, per_page=10):
        if type(run_id) in (tuple, list):
            run_id = ','.join(str(ri) for ri in run_id)

        if connection_id and not run_id:
            url = f"{self.BACKEND_URL}/api/servers/{connection_id}/runs/?page={page}&per_page={per_page}"

        else:
            url = f"{self.BACKEND_URL}/api/pipeline_runs/?page={page}&per_page={per_page}"
            if run_id:
                url += f"&run_id={run_id}"

        return self.call_backend("get", url)

    def get_interface_runs(self, interface_id=None, page=1, per_page=10):
        url = (
            f"{self.BACKEND_URL}/api/interface_runs/?"
            f"interface_id={interface_id}&page={page}&per_page={per_page}"
        )
        return self.call_backend("GET", url)

    def get_interface_run(self, run_id):
        if not run_id:
            raise PeliqanClientException("'run_id' must be provided")

        url = f"{self.BACKEND_URL}/api/interface_runs/{run_id}/"
        return self.call_backend("GET", url)

    def get_interface_run_logs(self, interface_run_id):
        if not interface_run_id:
            raise PeliqanClientException("'interface_run_id' must be provided")

        url = f"{self.BACKEND_URL}/api/interface_runs/{interface_run_id}/logs/"
        return self.call_backend("get", url)

    def send_connection_invite(self, recipient, subject, message, confirmation_recipient, server_type):
        data = {
            'recipient': recipient,
            'subject': subject,
            'message': message,
            'confirmationRecipient': confirmation_recipient,
            'serverType': server_type,
        }

        url = f"{self.BACKEND_URL}/api/servers/invite/"

        return self.call_backend("POST", url, expected_status_code=204, json=data)

    def trigger_interface_run(self, interface_name, interface_id):
        interface_id = self._get_resource_id(
            resource_id=interface_id,
            resource_name=interface_name,
            resource_type='interface'
        )

        # create the script file
        url = f"{self.BACKEND_URL}/api/interfaces/trigger_run/{interface_id}/?shell=1"
        self.call_backend(
            "get",
            url,
            expected_status_code=200
        )

        url = f"{self.BACKEND_URL}/api/interface_runs/"
        return self.call_backend(
            "post",
            url,
            expected_status_code=201,
            json={'interface_id': interface_id, 'run_mode': 'SHELL', 'source': 'SCRIPT'}
        )

    def stop_interface_run(self, run_id):
        url = f"{self.BACKEND_URL}/api/interface_runs/{run_id}/"
        return self.call_backend("patch", url, json={'status': "STOPPING"})

    def get_interface_run_status(self, interface_run_id, timeout=None):
        url = f"{self.BACKEND_URL}/api/interface_runs/{interface_run_id}/"
        return self.call_backend("get", url)

    def get_secret(self, secret_id):
        url = f"{self.BACKEND_URL}/api/resource/secrets/{secret_id}/"
        return self.call_backend("get", url)

    def get_connection_state(self, connection_id):
        url = f"{self.BACKEND_URL}/api/servers/{connection_id}/pipeline/state/"
        return self.call_backend("get", url)

    def set_connection_state(self, connection_id, state):
        url = f"{self.BACKEND_URL}/api/servers/{connection_id}/pipeline/state/"
        return self.call_backend("post", url, json=state)

    def discover_pipeline(self, connection_id, streams, merge_schema):
        url = f"{self.BACKEND_URL}/api/servers/{connection_id}/pipeline/discover/"
        data = {}
        if streams:
            data['streams'] = streams

        if merge_schema is None:
            data['merge_schema'] = merge_schema

        return self.call_backend("post", url, json=data)

    def delete_table(self, table_id, force=False):
        url = f"{self.BACKEND_URL}/api/database/tables/{table_id}/"
        return self.call_backend("delete", url, json={'force': force}, expected_status_code=204)
