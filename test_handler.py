# test_handler.py
from moto import mock_dynamodb2,mock_lambda, mock_iam,mock_s3
import boto3
from boto3.dynamodb.conditions import Attr, Key
import pytest
import json
import os
from unittest import mock, TestCase
from handler import addNewEventMessage


@pytest.fixture
def event():
    return {"body":{}}

@pytest.fixture
def context():
    return {}

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'

@mock.patch.dict(os.environ,{'eventTable':'event-dev'})
@mock_dynamodb2
def test_handler_add_new_event_message(aws_credentials):
    table_name= 'event-dev'
    conn = boto3.resource('dynamodb', region_name='ap-southeast-2')

    table = conn.create_table(
        TableName='event-dev',
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'},
                    {'AttributeName': 'date', 'KeyType': 'RANGE'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'},
                                {'AttributeName': 'date', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1},
        StreamSpecification={
            'StreamEnabled': True,
            'StreamViewType': 'NEW_IMAGE'
        }
    )

    eventBodyJson = json.dumps({"date":"2019-08-20", "location":"Bathroom" })
    eventBody = {"body":eventBodyJson}
    response = addNewEventMessage(eventBody,{})

    assert response['statusCode'] == 200
    new_event = json.loads(response['body'])
    id = new_event['id']
    date = new_event['date']

    query_results = table.query(
        KeyConditionExpression=Key('id').eq(id),
        ProjectionExpression='#d',
        ExpressionAttributeNames={
            '#d': date,
        },
    )

    assert query_results['Count'] > 0
