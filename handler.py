import json
from binance.client import Client

def binance_signal(event, context):
    
    client = Client()
    
    klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_4HOUR, "two week ago")
    
    def sma(n):
        return sum([float(k[4]) for k in klines[-n-1:-1]])/n
    
    def prev_sma(n):
        return sum([float(k[4]) for k in klines[-n-2:-2]])/n
    
    sma60 = sma(65)
    sma5 = sma(5)
    
    psma60 = prev_sma(65)
    psma5 = prev_sma(5)
    
    ret = ''
    
    if sma5 > sma60 and psma5 < psma60:
        ret = 'flip to long'
        
    if sma5 < sma60 and psma5 > psma60:
        ret = 'flip to short'
        
    if sma5 < sma60 and psma5 < psma60:
        ret = 'hold short'
    
    if sma5 > sma60 and psma5 > psma60:
        ret = 'hold long'

    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('btc-trading-signal: ' + ret)
    }
