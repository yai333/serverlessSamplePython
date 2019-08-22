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
    try:
        dbclient = boto3.client('stepfunctions')
        data = event['Records']
        inputData = data[0]['dynamodb']['NewImage']
        table = data[0]['eventSourceARN'].split(':')[5].split('/')[1]

        if data[0]['eventName'] == "INSERT":
            response = dbclient.start_execution(
                        stateMachineArn =os.environ['statemachineArn'],
                        input = json.dump(inputData)
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
    print(event)
    return
