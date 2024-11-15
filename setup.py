import os
import pika
from dotenv import load_dotenv

load_dotenv()

# RabbitMQ connection parameters
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
EXCHANGE_NAME = os.getenv('EXCHANGE_NAME')
QUEUE_NAMES = ['sms', 'mail', 'whatsapp']
DLX_NAME = os.getenv('DLX_NAME')
DLQ_NAME = os.getenv('DLQ_NAME')

# Establish connection to RabbitMQ
credentials = pika.PlainCredentials(username='username', password='password')
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
channel = connection.channel()

# Declare a topic exchange
channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic')
channel.exchange_declare(exchange=DLX_NAME, exchange_type='direct')

# Declare DLQ and DLX
channel.queue_declare(queue=DLQ_NAME, durable=True)
channel.queue_bind(exchange=DLX_NAME, queue=DLQ_NAME, routing_key='')

# Declare separate queues for each routing key and bind them
for queue_name in QUEUE_NAMES:
    channel.queue_declare(queue=queue_name, durable=True, arguments={
        'x-dead-letter-exchange': DLX_NAME,  # Specify the DLX for the queue
        'x-delivery-limit': 3,  # Set max retry count to 3
        'x-queue-type': 'quorum'
    })
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name, routing_key=queue_name)

print("Queues setup completed. Each queue is bound to its specific topic routing key.")
