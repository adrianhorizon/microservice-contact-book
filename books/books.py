import json
import logging
import os
import time
import uuid

import boto3
from books import decimalencoder

dynamodb = boto3.resource('dynamodb')

BOOK_TABLE = dynamodb.Table(os.environ['BOOK_TABLE'])
IS_OFFLINE = os.environ.get('IS_OFFLINE')

if IS_OFFLINE:
    client = boto3.client(
        'dynamodb',
        region_name='localhost',
        endpoint_url='http://localhost:8000'
    )
else:
    client = boto3.client('dynamodb')


def get_book(event, context):
    result = client.get_item(
        TableName=BOOK_TABLE,
        Key={
            'bookId': event['pathParameters']['bookId']
        }
    )

    response = {
        "statusCode": 200,
        "body": json.dumps(result['Item'],
                           cls=decimalencoder.DecimalEncoder)
    }

    return response


def list_book(event, context):
    result = client.scan(TableName=BOOK_TABLE)

    response = {
        "statusCode": 200,
        "body": json.dumps(result['Items'], cls=decimalencoder.DecimalEncoder)
    }

    return response


def create_book(event, context):
    data = json.loads(event['body'])
    if 'text' not in data:
        logging.error("Validation Failed")
        raise Exception("Couldn't create the todo item.")

    timestamp = str(time.time())

    item = {
        'bookId': str(uuid.uuid1()),
        'text': data['text'],
        'checked': False,
        'createdAt': timestamp,
        'updatedAt': timestamp,
    }

    client.put_item(TableName=BOOK_TABLE,Item=item)

    response = {
        "statusCode": 200,
        "body": json.dumps(item)
    }

    return response


def update_book(event, context):
    data = json.loads(event['body'])
    if 'text' not in data or 'checked' not in data:
        logging.error("Validation Failed")
        raise Exception("Couldn't update the todo item.")
        return

    timestamp = int(time.time() * 1000)

    result = client.update_item(
        TableName=BOOK_TABLE,
        Key={
            'bookId': event['pathParameters']['bookId']
        },
        ExpressionAttributeNames={
          '#todo_text': 'text',
        },
        ExpressionAttributeValues={
          ':text': data['text'],
          ':checked': data['checked'],
          ':updatedAt': timestamp,
        },
        UpdateExpression='SET #todo_text = :text, '
                         'checked = :checked, '
                         'updatedAt = :updatedAt',
        ReturnValues='ALL_NEW',
    )

    response = {
        "statusCode": 200,
        "body": json.dumps(result['Attributes'],
                           cls=decimalencoder.DecimalEncoder)
    }

    return response


def delete_book(event, context):
    client.delete_item(
        TableName=BOOK_TABLE,
        Key={
            'bookId': event['pathParameters']['bookId']
        }
    )

    response = {
        "statusCode": 200
    }

    return response
