import boto3
import botocore
import pytest_boto_mock


def test_version():
    assert hasattr(pytest_boto_mock, '__version__')
    assert type(pytest_boto_mock.__version__) is str


def test_boto3_version():
    assert hasattr(boto3, '__version__')
    assert type(boto3.__version__) is str


def test_botocore_version():
    assert hasattr(botocore, '__version__')
    assert type(botocore.__version__) is str
