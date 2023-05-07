import os
import boto3
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

def handle_api_gateway_event(event):
    # Handle requests from discord interaction endpoint
    command = event['pathParameters']['command']
    client = discord.Client()
    client.run(os.environ['DISCORD_BOT_TOKEN'])
    bot.invoke(client.get_context(event))
    return {
        'statusCode': 200,
        'body': 'Discord command handled successfully!'
    }

def handle_trade_bot_event(event):
    # Handle requests from trade_bot
    message = event['detail']['message']
    client = discord.Client()
    client.run(os.environ['DISCORD_BOT_TOKEN'])
    channel = client.get_channel(int(os.environ['DISCORD_CHANNEL_ID']))
    channel.send(message)
    return {
        'statusCode': 200,
        'body': 'trade_bot request handled successfully!'
    }

def handler(event, context):
    try:
        if "httpMethod" in event and event["httpMethod"] == "POST":
            return handle_api_gateway_event(event)
        elif "source" in event and event["source"] == "trade_bot":
            return handle_trade_bot_event(event)
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }