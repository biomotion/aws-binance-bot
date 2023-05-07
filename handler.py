import json
from binance.client import Client

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

def handle_eventbridge_event(event):
    # Handle requests from EventBridge
    ret = get_indicator()
    return {
        'statusCode': 200,
        'body': json.dumps('btc-trading-signal: ' + ret)
    }

def handle_api_gateway_event(event):
    # Handle requests from discord_bot
    pass

def binance_trade(event, context):
    if "source" in event and event["source"] == "polling":  # EventBridge event
        handle_eventbridge_event(event)
    elif "httpMethod" in event:  # API Gateway event
        handle_api_gateway_event(event)