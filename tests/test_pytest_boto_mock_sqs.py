import uuid

import boto3
import pytest


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
