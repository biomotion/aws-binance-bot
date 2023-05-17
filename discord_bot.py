import os
import boto3
import json
import requests
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
SCHEDULE_RULE_NAME = os.environ.get('SCHEDULE_RULE_NAME')
PUBLIC_KEY = os.environ.get('PUBLIC_KEY')

def send_message_to_discord_channel(channel_id, message_content):
    url = f'https://discord.com/api/v10/channels/{channel_id}/messages'
    headers = {
        'Authorization': f'Bot {DISCORD_BOT_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'content': message_content,
        'tts': False
    }
    response = requests.post(url, json=data, headers=headers)

    if response.status_code != 200:
        raise ValueError(f'Error sending message: {response.status_code} {response.text}')

def handle_api_gateway_event(event):
    # Handle requests from discord interaction endpoint
    event_bridge = boto3.client('events')
    print(event)

    # validate the interaction
    signature = event['headers']['x-signature-ed25519']
    timestamp = event['headers']['x-signature-timestamp']
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    message = "{}{}".format(timestamp, event['body'])
    try:
      verify_key.verify(message.encode(), signature=bytes.fromhex(signature))
    except BadSignatureError:
      print("invalid request signature")
      return {
        'statusCode': 401,
        'body': json.dumps('invalid request signature')
      }
    body = json.loads(event['body'])
    print("TYPE: ", body['type'])
    if body['type'] == 1:
        print("returning type 1")
        return {
            'statusCode': 200,
            'body': json.dumps({
                'type': 1
            })
        }
    elif body['type'] == 2:
        print("returning type 2")
        channel_id = body['channel_id']
        data = body['data']
        if data['name'] == 'start':
            event_bridge.enable_rule(
                Name=SCHEDULE_RULE_NAME
            )
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'type': 4,
                    'data': {'content': "rule is enabled"}
                })
            }
            # send_message_to_discord_channel(channel_id, "rule is enabled")
        elif data['name'] == 'stop':
            event_bridge.disable_rule(
                Name=SCHEDULE_RULE_NAME
            )
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'type': 4,
                    'data': {'content': "rule is disabled"}
                })
            }
            # send_message_to_discord_channel(channel_id, "rule is disabled")
        else:
            # send_message_to_discord_channel(channel_id, "Invalid command")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'type': 4,
                    'data': {'content': 'Invalid command'}
                })
            }

def handle_trade_bot_event(event):
    # Handle requests from trade_bot
    channel_id = os.environ.get('DISCORD_CHANNEL_ID')
    message_content = event['detail'].get('message', '')
    if message_content == '':
        raise ValueError('Message content is empty')
    send_message_to_discord_channel(channel_id, message_content)

def handler(event, context):
    if 'httpMethod' in event and event['httpMethod'] == 'POST':
        print("handling api gateway event")
        ret = handle_api_gateway_event(event)
        print("RET: ", ret)
        return ret
    elif 'source' in event and event['source'] == 'trade_bot':
        print("handling trade bot event")
        return handle_trade_bot_event(event)
    else:
        return {
            'statusCode': 500,
            'body': 'Invalid request'
        }