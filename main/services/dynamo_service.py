# services/dynamo_service.py

import boto3
import boto3

# Create the DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TestRuns')  # replace with your actual table name


def insert_item(item: dict):
    """
    Inserts a single item into the TestRuns DynamoDB table.
    """
    response = table.put_item(Item=item)
    return response


def get_item(test_id: str, sk: str):
    """
    Gets a specific item by primary key (TestID + SK).
    """
    response = table.get_item(
        Key={
            'TestID': test_id,
            'SK': sk
        }
    )
    return response.get('Item')


def query_all_items_for_test(test_id: str):
    """
    Gets all items for a specific test_id (partition key).
    """
    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('TestID').eq(test_id)
    )
    return response.get('Items', [])
