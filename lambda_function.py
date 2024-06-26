import json
import urllib.request
import os
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

MAX_TOKENS=150
SLACK_POST_URL = os.environ["WEB_HOOK_URL_DEV"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SQS_URL = os.environ["SQS_URL"]

modelId='anthropic.claude-v2'
accept = 'application/json'
contentType = 'application/json'

bedrock = boto3.client('bedrock-runtime')


def lambda_handler(event, context):
    
    logger.info('event: %s', event)
    
    user_prompt = event['event']['text']
    channel = event['event']['channel']
    user = event['event']['user']
    
    logger.info('Body: %s', user_prompt)
    logger.info('Channel: %s', channel)
    
    message = calling_bedrock(user_prompt)
    response = format_webhook(user, message)
    
    post_message_to_slack(response)


def exception_handler(e, status_code, message):
    # exception to status code mapping goes here...
    return  {
        
        'statusCode': status_code,
        'body': json.dumps(str(e)),
        'message': message
    }
    
    
def format_webhook(user, message):
    
     message_response = {
         "text": '<@' + user + '>' + message
     }
     
     return message_response
     
     
def format_post_message(user, channel, message):
    
     message_response = {
         
         "channel": channel,
         "text": '<@' + user + '> ' + message
     }
     
     return message_response



def calling_bedrock(prompt_data):  
    
    #formatting body for claude
    body = json.dumps({"prompt": "Human:"+prompt_data+"\nAssistant:", "max_tokens_to_sample":MAX_TOKENS})
    logger.info('Amazon Bedrock prompt: %s', body)
    
    #invoke model
    try:
        logger.info('Calling Amazon Bedrock API')
        response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    except Exception as e:
        logger.error('Failed to execute call to Amazon Bedrock! Error: %s', str(e))
        return exception_handler(e, 500, 'Failed to execute call to Amazon Bedrock!')
    
    if 'body' in response and response['body'] is not None:
        response_body = json.loads(response['body'].read())
        message = response_body.get('completion', 'Error: Unexpected Bedrock response format.')
        logger.info('Bedrock response: %s', message)
        return message
    else:
        logger.error('Invalid Bedrock response')
        return exception_handler(ValueError("Invalid Bedrock response"), 500, 'Failed to execute Bedrock call!')


def post_message_to_slack(response):
    
    logger.info('Message for post message: %s', response)
    
    try:
        hdr = {'Content-Type': 'application/json; charset=utf-8'}
        req = urllib.request.Request(SLACK_POST_URL, json.dumps(response).encode('utf-8'), hdr)
        response_webhook = urllib.request.urlopen(req).read()
        logger.info('message for post message: %s', response_webhook)
    except Exception as e:
        logger.error('Failed to execute the function! Error: %s', str(e))
        return exception_handler(e, 500, 'Failed to execute the function! Please, try again!')


 
    
#SLACK - Event subscription challenge validator

#def lambda_handler(event, context):
    
  
  
#     return {
#     "statusCode": 200,
#     "body": json.dumps(event)
#     }


# Working with stream
 # stream = response.get('body')
        
        # if stream:
        #     for event in stream:
        #         chunk = event.get('chunk')
        #         if chunk:
        #             print(json.loads(chunk.get('bytes').decode()))
        #             message = json.loads(chunk.get('bytes').decode())
        #             response = message['completion']
                    
        #         print('Bedrock stream response: {}'.format(response))
        
        # return response

#message = 'Hello teste!'
#response = format_post_message(user, channel, message)
