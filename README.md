# Customer Service AI Bot

## Objective
Customer Service AI Bot enables businesses to provide an intelligent agent, able to support customers nearly as effectively as a human customer support agent. 
The AI bot integrates with business logic and guidelines to work with the product issues that a customer is dealing with while only referencing business rules to do so.
This strongly improves the bandwidth of support operations, maintains business integrity with the customer and alleviates incidents nearly as effectively as manual customer support.
The implementation for this application is free for small-scale applications and handles large-scale flows for very cheap.

## User Flow
- User has query and navigates to the company site page to interact with the Customer Service bot.
- User initiates a Websocket connection from the client and has their connection saved to the DB.
- User writes query with a <code>sendMessage</code> route
- Customer Service bot takes the business prompt, chat history and user prompt to respond with relevant information to the business, bridging support for customer with business rules and guidelines.
  
## Implementation
The bot is fully implemented in AWS and can be integrated seamlessly into any web or mobile applications. Technologies include API Gateway for Websocket routing and middleware,
Lambda for handling chat and model logic, Bedrock for LLM invocation and DynamoDB for storing user chat history.

I'm using the [Llama 3.3 7B Instruct](https://us-east-2.console.aws.amazon.com/bedrock/home?region=us-east-2#/model-catalog/serverless/meta.llama3-3-70b-instruct-v1:0) model as part of Bedrock; cheap to use for large-scale applications. 
This model is stateless, serverless, lacks built-in chat understanding and lacks role-seperation. To address this, I created a prompt where it learned it was an assistant and would take chat history from DynamoDB as context for generation.

DynamoDB will take a <code>userId</code> as a partition key and a <code>sessionId</code> as a sort key where the sessionId is the Websocket connectionId. As the system grows, it will handle a large volume of users thanks to fast reads and writes.
DynamoDB will index on data by userId while supporting multiple chat histories enabling fast retrieval of a chat. I asynchronously write chat data to Dynamo while the AI bot response is sent back to the user, keeping response times low.
