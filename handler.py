import json
import logging
import boto3
import os
import uuid
import datetime
from boto3.dynamodb.types import TypeDeserializer

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
serializer = TypeDeserializer()

def addNewEventMessage(event, context):
    dynamodb = boto3.resource('dynamodb')
    data = json.loads(event['body'])

    if 'location' not in data:
        logging.error("Validation Failed")

    table = dynamodb.Table(os.environ['eventTable'])

    item = {
        'id': str(uuid.uuid4()),
        'date': data['date'],
        'location': data['location']
    }


    table.put_item(Item=item)

    response = {
        "statusCode": 200,
        "body": json.dumps(item)
    }

    return response

def addNewActivityMessage(event, context):
    dynamodb = boto3.resource('dynamodb')
    data = json.loads(event['body'])

    if 'location' not in data:
        logging.error("Validation Failed")
        raise Exception("Couldn't create the activity item.")


    table = dynamodb.Table(os.environ['activityTable'])

    item = {
        'id': str(uuid.uuid4()),
        'date': data['date'],
        'location': data['location']
    }


    table.put_item(Item=item)

    response = {
        "statusCode": 200,
        "body": json.dumps(item)
    }

    return response

def newMessageEventListener(event, context):
    try:
        dbclient = boto3.client('stepfunctions')
        data = event['Records']

        inputData = data[0]['dynamodb']['NewImage']
        inputData = deserialize(inputData)
        table = data[0]['eventSourceARN'].split(':')[5].split('/')[1]
        inputData['table'] = table
        print(inputData)
        if data[0]['eventName'] == "INSERT":
            response = dbclient.start_execution(
                        stateMachineArn = os.environ['statemachineArn'],
                        input = json.dumps(inputData)
                    )
        return
    except Exception as e:
        logging.error(e)
        return

def caculateInsightOne(event, context):
    print(event)
    logging.info("Calcate Insight one")
    return


def caculateInsightTwo(event, context):
    print(event)
    logging.info("Calcate Insight two")
    return

def syncDBToS3(event, context):
    s3 = boto3.resource('s3')

    if (event['table']=='event-dev'):
       bucket = os.environ['eventBucket']
    else:
       bucket = os.environ['activityBucket']

    today = datetime.datetime.now()
    key =  f'{event["id"]}-{today:%Y-%m-%dT%H:%M%S}'

    s3.Object(bucket, key).put(Body=(json.dumps(event)))
    return

def deserialize(data):
    if isinstance(data, list):
       return [deserialize(v) for v in data]

    if isinstance(data, dict):
        try:
            return serializer.deserialize(data)
        except TypeError:
            return { k : deserialize(v) for k, v in data.items() }
    else:
        return data
