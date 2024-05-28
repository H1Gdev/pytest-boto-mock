import io
import json

import botocore
import botocore.client
import pytest


class BotoMockerFixture:
    # Botocore
    _make_api_call = botocore.client.BaseClient._make_api_call

    def __init__(self, mocker):
        self.mocker = mocker

    def patch(self, new):
        self.mocker.patch('botocore.client.BaseClient._make_api_call', new=new)

    @staticmethod
    def build_make_api_call(service_table):
        def make_api_call(self, operation_name, kwarg):
            service_name = type(self).__name__.lower()

            operation_table = service_table.get(service_name)
            if operation_table is not None and operation_name in operation_table:
                operation = operation_table.get(operation_name)
                if isinstance(operation, Exception):
                    raise operation
                return operation(self, operation_name, kwarg) if callable(operation) else operation
            return BotoMockerFixture._make_api_call(self, operation_name, kwarg)

        return make_api_call

    @staticmethod
    def build_lambda_invoke_handler(response_table):
        def handle_lambda_invoke(self, operation_name, kwarg):
            function_name = kwarg.get('FunctionName')

            response = response_table.get(function_name)
            if response is not None:
                payload = response.get('Payload')
                if isinstance(payload, Exception):
                    if 'FunctionError' in response:
                        payload = {'errorMessage': str(payload), 'errorType': type(payload).__name__}
                    else:
                        raise payload
                if payload:
                    payload = json.dumps(payload)
                payload = payload.encode()
                return response | {
                    'Payload': botocore.response.StreamingBody(io.BytesIO(payload), len(payload))
                }
            return BotoMockerFixture._make_api_call(self, operation_name, kwarg)

        return handle_lambda_invoke


# For all scopes.
boto_mocker = pytest.fixture()(lambda mocker: BotoMockerFixture(mocker))
class_boto_mocker = pytest.fixture(scope='class')(lambda class_mocker: BotoMockerFixture(class_mocker))
module_boto_mocker = pytest.fixture(scope='module')(lambda module_mocker: BotoMockerFixture(module_mocker))
package_boto_mocker = pytest.fixture(scope='package')(lambda package_mocker: BotoMockerFixture(package_mocker))
session_boto_mocker = pytest.fixture(scope='session')(lambda session_mocker: BotoMockerFixture(session_mocker))
