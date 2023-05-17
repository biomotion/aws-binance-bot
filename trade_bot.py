import json
from binance.client import Client
import boto3

client = Client()
    
def get_indicator():
    
    klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_4HOUR, "two week ago")
    
    def sma(n):
        return sum([float(k[4]) for k in klines[-n-1:-1]])/n
    
    def prev_sma(n):
        return sum([float(k[4]) for k in klines[-n-2:-2]])/n
    
    sma60 = sma(65)
    sma5 = sma(5)
    
    psma60 = prev_sma(65)
    psma5 = prev_sma(5)
    
    if sma5 > sma60 and psma5 < psma60:
        return 'flip to long'
        
    if sma5 < sma60 and psma5 > psma60:
        return 'flip to short'
        
    if sma5 < sma60 and psma5 < psma60:
        return 'hold short'
    
    if sma5 > sma60 and psma5 > psma60:
        return 'hold long'

def handle_polling_event(event):
    # Handle requests from EventBridge
    ret = get_indicator()
    event_bridge = boto3.client('events')
    event_detail = {
        'message': ret
    }
    print(event_detail)
    response = event_bridge.put_events(
        Entries=[
            {
                'Source': 'trade_bot',
                'DetailType': 'TradeBotRequest',
                'Detail': json.dumps(event_detail),
            }
        ]
    )

    if response['FailedEntryCount'] > 0:
        raise Exception('Failed to send message to EventBridge')
    else:
        return {
            'statusCode': 200,
            'body': json.dumps('Message sent to EventBridge')
        }

def handler(event, context):
    if 'source' in event and event["source"] == "polling":  # EventBridge event
        print("polling event")
        return handle_polling_event(event)
    else:
        return {
            'statusCode': 400,
            'body': 'Invalid request'
        }