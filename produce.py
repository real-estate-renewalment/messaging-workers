#!/usr/bin/env python
import json
import os
import pika
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
EXCHANGE = os.getenv('EXCHANGE_NAME')

credentials = pika.PlainCredentials(username='username', password='password')
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
channel = connection.channel()

message = {
    'url': WEBHOOK_URL,
    'body': {
        'a': 1,
        'b': 'test'
    }
}
channel.basic_publish(exchange=EXCHANGE, routing_key='', body=json.dumps(message))
print(f" [x] Sent {message}")
connection.close()