import json
import boto3

bedrock = boto3.client("bedrock-runtime")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Conversations")
lambda_client = boto3.client("lambda")
apigw = boto3.client("apigatewaymanagementapi", endpoint_url="")

def get_request_body(event):
    if isinstance(event['body'], str):
        return json.loads(event['body'])  # Convert string to JSON
    else:
        return event['body']
    
def mock_lambda_invoke(event):
    connection_id = event["requestContext"]["connectionId"]
    request_body = get_request_body(event)
    user_message = request_body.get("message", "")
    return {
            "statusCode": 200,
            "body": json.dumps({"mockedResponse": "Testing without Bedrock."})
        }

def invoke_bedrock(prompt):
    payload = {
            "prompt": prompt,
            "temperature": 0.7,
            "top_p": 0.9
        }
    response = bedrock.invoke_model(
        modelId="meta.llama3-3-70b-instruct-v1:0",
        body=json.dumps(payload)
    )
    return json.loads(response["body"].read())

def async_write_to_dynamo(request_body, connection_id, message):
    payload = {
            "userId": str(request_body.get("userId")),
            "sessionId": connection_id,
            "history": message 
        }
    lambda_client.invoke(
        FunctionName="asyncWriteConvoToDB",
        InvocationType="Event",
        Payload=json.dumps(payload)
    )

def get_history(user_id, connection_id):
    response = table.get_item(
        Key={
            "userId": user_id,
            "sessionId": connection_id
        }
    )
    return response.get("Item", {}).get("history", "")

def build_prompt(chat_history, user_message):
    if not chat_history: chat_history = []
    chat_history += [user_message]

    return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a helpful and concise customer service agent. Use the rules and suggestions below to assist the user.

    Business Rules:
    - No refunds or returns after 7 days.
    - Product must not be used before return.

    Problem-Solving Suggestions:
    - Ask if the product was marked as delivered.
    - Ask for the order ID.

    Company Guidelines:
    - Order what makes you happy.
    - Always ask for more details if needed.

    <|eot_id|>
    <|start_header_id|>user<|end_header_id|>
    {chat_history}
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>"""

def lambda_handler(event, context):
    try:
        connection_id = event["requestContext"]["connectionId"]
        request_body = get_request_body(event)
        
        user_message = request_body.get("message", "")
        user_id = request_body.get("userId")

        chat_history = get_history(user_id, connection_id)
        prompt = build_prompt(chat_history, user_message)

        response_body = invoke_bedrock(prompt)
        async_write_to_dynamo(request_body, connection_id, response_body)
        async_write_to_dynamo(request_body, connection_id, user_message)

        return {
            "statusCode": 200,
            "body": json.dumps(response_body)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }