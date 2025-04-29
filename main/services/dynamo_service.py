import boto3

def get_dynamo_table():
    session = boto3.Session(profile_name="niv-aws-academy")
    dynamodb = session.resource("dynamodb")  # or use session.client("dynamodb")
    return dynamodb.Table('TestRuns')

def insert_item(item: dict):
    table = get_dynamo_table()
    response = table.put_item(Item=item)
    return response


def get_item(test_id: str, sk: str):
    table = get_dynamo_table()
    response = table.get_item(
        Key={
            'TestID': test_id,
            'SK': sk
        }
    )
    return response.get('Item')

def query_all_items_for_test(test_id: str):
    table = get_dynamo_table()
    from boto3.dynamodb.conditions import Key  # (small fix here too)
    response = table.query(
        KeyConditionExpression=Key('TestID').eq(test_id)
    )
    return response.get('Items', [])
