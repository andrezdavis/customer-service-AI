import json
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Conversations")

def writeMessageToDB(event):
    response = table.update_item(
        Key={
            'userId': event['userId'],
            'sessionId': event['sessionId']
        },
        UpdateExpression="SET history = list_append(if_not_exists(history, :empty_list), :msg)",
        ExpressionAttributeValues={
            ":msg": [event['history']],
            ":empty_list": []  # This will be used if the attribute doesn't exist
            },  # Must be a list
        ReturnValues="UPDATED_NEW"
    )
    return response

def lambda_handler(event, context):
    # Write response to DynamoDB
    try:
        writeMessageToDB(event)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Saved to DynamoDB"})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }