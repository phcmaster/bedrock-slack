import json
import urllib.request
import os
import boto3
import logging


MAX_TOKENS=150
SLACK_POST_URL = os.environ["WEB_HOOK_URL_DEV"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SQS_URL = os.environ["SQS_URL"]

modelId='anthropic.claude-v2'
accept = 'application/json'
contentType = 'application/json'

bedrock = boto3.client('bedrock-runtime')


def lambda_handler(event, context):
    
    print("evento: {}".format(event))
    
    user_prompt = event['event']['text']
    channel = event['event']['channel']
    user = event['event']['user']
    
    print("Body: {}".format(user_prompt))
    print("Channel: {}".format(channel))
    
    message = calling_bedrock(user_prompt)
    
    #message = 'Hello teste!'
    
    #response = format_post_message(user, channel, message)
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
    
    print('Calling Amazon Bedrock API')
    
    #formatting body for claude
    body = json.dumps({"prompt": "Human:"+prompt_data+"\nAssistant:", "max_tokens_to_sample":MAX_TOKENS})
    
    print('Bedrock body: {}'.format(body))
    
    #invoke model
    try:
        response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    except Exception as e:
        return exception_handler(e, 500, 'Falha ao executar chamada para o Bedrock!')
    
    if 'body' in response and response['body'] is not None:
        response_body = json.loads(response['body'].read())
        message = response_body.get('completion', 'Error: Unexpected Bedrock response format.')
        print('Bedrock response: {}'.format(message))
        return message
    else:
        return exception_handler(ValueError("Invalid Bedrock response"), 500, 'Failed to execute Bedrock call!')


def post_message_to_slack(response):
    
    print("message for post message: {}".format(response))
    
    try:
        #hdr = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': 'Bearer ' + SLACK_BOT_TOKEN}
        hdr = {'Content-Type': 'application/json; charset=utf-8'}
        req = urllib.request.Request(SLACK_POST_URL, json.dumps(response).encode('utf-8'), hdr)
        response_webhook = urllib.request.urlopen(req).read()
        logger.info("message for post message: {}".format(response_webhook))
    except Exception as e:
        return exception_handler(e, 500, 'Falha ao executar a função! Tente novamente!')


 
 
 
    
#SLACK - Event subscription challenge validator

#def lambda_handler(event, context):
    
  
  
#     return {
#     "statusCode": 200,
#     "body": json.dumps(event)
#     }



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