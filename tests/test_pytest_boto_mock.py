import uuid
import json

import boto3
import botocore.exceptions
import pytest


# Lambda
def test_lambda_call_native(boto_mocker):
    boto_mocker.patch(new=boto_mocker.build_make_api_call({
    }))

    with pytest.raises(botocore.exceptions.ParamValidationError):
        boto3.client('lambda').invoke()


@pytest.mark.parametrize('expected', [
    None,
    'Test',
    {},
    {'StatusCode': 200, 'Payload': json.dumps({}).encode()},
])
def test_lambda_value(boto_mocker, expected):
    boto_mocker.patch(new=boto_mocker.build_make_api_call({
        'lambda': {'Invoke': expected}
    }))

    actual = boto3.client('lambda').invoke(FunctionName='FunctionName')
    assert actual == expected


@pytest.mark.parametrize('expected', [
    None,
    'Test',
    {},
    {'StatusCode': 200, 'Payload': json.dumps({}).encode()},
])
def test_lambda_callable(boto_mocker, expected):
    def callable(self, operation_name, kwarg):
        return expected

    boto_mocker.patch(new=boto_mocker.build_make_api_call({
        'lambda': {'Invoke': callable}
    }))

    actual = boto3.client('lambda').invoke(FunctionName='FunctionName')
    assert actual == expected


@pytest.mark.parametrize('expected', [
    Exception(),
    botocore.exceptions.ClientError({}, 'Invoke'),
])
def test_lambda_exception(boto_mocker, expected):
    boto_mocker.patch(new=boto_mocker.build_make_api_call({
        'lambda': {'Invoke': expected}
    }))

    with pytest.raises(Exception) as ex:
        boto3.client('lambda').invoke(FunctionName='FunctionName')
        assert ex == expected


@pytest.mark.parametrize('expected', [
    # lambda_handler return value format.
    {'statusCode': 200, 'body': json.dumps('Hello from Lambda!')},
    '',
])
def test_lambda_invoke_value(boto_mocker, expected):
    boto_mocker.patch(new=boto_mocker.build_make_api_call({
        'lambda': {
            'Invoke': boto_mocker.build_lambda_invoke_handler({
                'FunctionName': {
                    'StatusCode': 200,
                    'Payload': expected,
                }
            })
        }
    }))

    response = boto3.client('lambda').invoke(FunctionName='FunctionName')
    assert response.get('StatusCode') == 200
    actual = response.get('Payload').read().decode()
    if actual:
        actual = json.loads(actual)
    assert actual == expected


@pytest.mark.parametrize('expected', [
    # lambda_handler return value format.
    {'statusCode': 200, 'body': json.dumps('Hello from Lambda!')},
    '',
])
def test_lambda_invoke_callable(boto_mocker, expected):
    def callable(self, operation_name, kwarg):
        return {
            'StatusCode': 200,
            'Payload': expected,
        }

    boto_mocker.patch(new=boto_mocker.build_make_api_call({
        'lambda': {
            'Invoke': boto_mocker.build_lambda_invoke_handler({
                'FunctionName': callable,
            })
        }
    }))

    response = boto3.client('lambda').invoke(FunctionName='FunctionName')
    assert response.get('StatusCode') == 200
    actual = response.get('Payload').read().decode()
    if actual:
        actual = json.loads(actual)
    assert expected == actual


@pytest.mark.parametrize('expected', [
    # lambda_handler return value format.
    {'statusCode': 200, 'body': json.dumps('Hello from Lambda!')},
    '',
])
def test_lambda_invoke_payload_callable(boto_mocker, expected):
    def callable(self, operation_name, kwarg):
        return expected

    boto_mocker.patch(new=boto_mocker.build_make_api_call({
        'lambda': {
            'Invoke': boto_mocker.build_lambda_invoke_handler({
                'FunctionName': {
                    'StatusCode': 200,
                    'Payload': callable,
                }
            })
        }
    }))

    response = boto3.client('lambda').invoke(FunctionName='FunctionName')
    assert response.get('StatusCode') == 200
    actual = response.get('Payload').read().decode()
    if actual:
        actual = json.loads(actual)
    assert expected == actual


@pytest.mark.parametrize('expected', [
    botocore.exceptions.ClientError({}, 'Invoke'),
])
def test_lambda_invoke_payload_exception(boto_mocker, expected):
    boto_mocker.patch(new=boto_mocker.build_make_api_call({
        'lambda': {
            'Invoke': boto_mocker.build_lambda_invoke_handler({
                'FunctionName': {
                    'StatusCode': 200,
                    'Payload': expected,
                }
            })
        }
    }))

    with pytest.raises(Exception) as ex:
        boto3.client('lambda').invoke(FunctionName='FunctionName')
        assert ex == expected


@pytest.mark.parametrize('expected', [
    Exception('error in lambda function'),
])
def test_lambda_invoke_function_error(boto_mocker, expected):
    boto_mocker.patch(new=boto_mocker.build_make_api_call({
        'lambda': {
            'Invoke': boto_mocker.build_lambda_invoke_handler({
                'FunctionName': {
                    'StatusCode': 200,
                    'FunctionError': 'Unhandled',
                    'Payload': expected,
                }
            })
        }
    }))

    response = boto3.client('lambda').invoke(FunctionName='FunctionName')
    assert response.get('StatusCode') == 200
    payload = json.loads(response.get('Payload').read())
    actual = payload.get('errorMessage')
    assert actual == str(expected)


def test_lambda_invoke_event(boto_mocker):
    boto_mocker.patch(new=boto_mocker.build_make_api_call({
        'lambda': {
            'Invoke': boto_mocker.build_lambda_invoke_handler({
                'FunctionName': {
                    'ResponseMetadata': {'HTTPStatusCode': 202},
                    'StatusCode': 202,
                    'Payload': '',
                }
            })
        }
    }))

    response = boto3.client('lambda').invoke(FunctionName='FunctionName', InvocationType='Event')
    assert response.get('StatusCode') == 202
    response.get('Payload').read()


# S3
def test_s3_call_native(boto_mocker):
    boto_mocker.patch(new=boto_mocker.build_make_api_call({
    }))

    with pytest.raises(botocore.exceptions.ParamValidationError):
        boto3.client('s3').copy_object()


@pytest.mark.parametrize('expected', [
    None,
    'Test',
    {},
    {'ResponseMetadata': {'HTTPStatusCode': 200}},
])
def test_s3_value(boto_mocker, expected):
    boto_mocker.patch(new=boto_mocker.build_make_api_call({
        's3': {'CopyObject': expected}
    }))

    actual = boto3.client('s3').copy_object(Bucket='bucket')
    assert actual == expected


@pytest.mark.parametrize('expected', [
    None,
    'Test',
    {},
    {'ResponseMetadata': {'HTTPStatusCode': 200}},
])
def test_s3_callable(boto_mocker, expected):
    def callable(self, operation_name, kwarg):
        return expected

    boto_mocker.patch(new=boto_mocker.build_make_api_call({
        's3': {'CopyObject': callable}
    }))

    actual = boto3.client('s3').copy_object(Bucket='bucket')
    assert actual == expected


@pytest.mark.parametrize('expected', [
    Exception(),
    botocore.exceptions.ClientError({}, 'CopyObject'),
])
def test_s3_exception(boto_mocker, expected):
    boto_mocker.patch(new=boto_mocker.build_make_api_call({
        's3': {'CopyObject': expected},
    }))

    with pytest.raises(Exception) as ex:
        boto3.client('s3').copy_object(Bucket='bucket')
        assert ex == expected


@pytest.mark.parametrize('count', [
    0,
    2,
])
def test_s3_resource(boto_mocker, count):
    def list_objects(self, operation_name, kwarg):
        ret = {
            'ResponseMetadata': {'HTTPStatusCode': 200},
            'IsTruncated': False,
            'Name': 'bucket',
            'Prefix': 'test',
            'MaxKeys': 1000,
        }
        if count:
            ret['Contents'] = [{'Key': f"test_{i}.txt"} for i in range(count)]
        return ret

    def delete_objects(self, operation_name, kwarg):
        ret = {
            'ResponseMetadata': {'HTTPStatusCode': 200},
        }
        if count:
            ret['Deleted'] = [{'Key': f"test_{i}.txt"} for i in range(count)]
        return ret

    boto_mocker.patch(new=boto_mocker.build_make_api_call({
        's3': {
            'ListObjects': list_objects,
            'DeleteObjects': delete_objects,
        },
    }))

    boto3.resource('s3').Bucket('bucket').objects.filter(Prefix='test').delete()


# SQS
@pytest.fixture
def setup_sqs(boto_mocker):
    """
    Setup Amazon SQS client.
    """
    message_list = {}

    def send_message(self, operation_name, kwarg):
        queue_url = kwarg['QueueUrl']
        message = {
            'Body': kwarg['MessageBody'],
            'ReceiptHandle': str(uuid.uuid4()),
        }

        nonlocal message_list
        if queue_url in message_list:
            message_list[queue_url].append(message)
        else:
            message_list[queue_url] = [message]

        return {
            'ResponseMetadata': {'HTTPStatusCode': 200},
        }

    def receive_message(self, operation_name, kwarg):
        queue_url = kwarg['QueueUrl']
        max_number_of_messages = kwarg.get('MaxNumberOfMessages', 1)

        nonlocal message_list
        ret = {
            'ResponseMetadata': {'HTTPStatusCode': 200},
        }
        messages = message_list[queue_url][:max_number_of_messages]
        if messages:
            ret['Messages'] = messages
        return ret

    def delete_message(self, operation_name, kwarg):
        queue_url = kwarg['QueueUrl']
        receipt_handle = kwarg['ReceiptHandle']

        nonlocal message_list
        message_list[queue_url] = [message for message in message_list[queue_url] if message['ReceiptHandle'] != receipt_handle]
        ret = {
            'ResponseMetadata': {'HTTPStatusCode': 200},
        }
        return ret

    boto_mocker.patch(new=boto_mocker.build_make_api_call({
        'sqs': {
            'SendMessage': send_message,
            'ReceiveMessage': receive_message,
            'DeleteMessage': delete_message,
        },
    }))


def test_sqs_sequence(setup_sqs):
    queue_url = 'https://sqs.REGION.amazonaws.com/ACCOUNT_ID/QueueName.fifo'
    sqs = boto3.client('sqs')
    response = sqs.send_message(QueueUrl=queue_url, MessageBody='Body', MessageGroupId='GroupId', MessageDeduplicationId='DeduplicationId')
    response = sqs.receive_message(QueueUrl=queue_url)
    receipt_handle = response['Messages'][0]['ReceiptHandle']
    response = sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
