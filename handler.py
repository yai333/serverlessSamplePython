import json
import logging
import boto3
import os
import uuid
from datetime import date

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')

def addNewEventMessage(event, context):
    data = json.loads(event['body'])

    if 'location' not in data:
        logging.error("Validation Failed")
        raise Exception("Couldn't create the event item.")


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
    logger.info("newMessageEventListener" + event )

def caculateInsightOne(event, context):
    logger.info("caculateInsightOne" + event )


def caculateInsightTwo(event, context):
    logger.info("caculateInsightTwo" + event )

def syncDBToS3(event, context):
    logger.info("caculateInsightTwo" + event )
