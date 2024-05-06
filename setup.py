import os
import pika
from dotenv import load_dotenv

load_dotenv()

# RabbitMQ connection parameters
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
EXCHANGE_NAME = os.getenv('EXCHANGE_NAME')
QUEUE_NAME = os.getenv('QUEUE_NAME')
DLX_NAME = os.getenv('DLX_NAME')
DLQ_NAME = os.getenv('DLQ_NAME')

# Establish connection to RabbitMQ
credentials = pika.PlainCredentials(username='username', password='password')
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
channel = connection.channel()


# Declare the DLX if it doesn't already exist
channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='direct')
channel.exchange_declare(exchange=DLX_NAME, exchange_type='direct')

# Declare the DLQ if it doesn't already exist
channel.queue_declare(queue=DLQ_NAME, durable=True)
channel.queue_bind(exchange=DLX_NAME, queue=DLQ_NAME, routing_key='')

# Configure the existing queue for dead-lettering with max retry count
channel.queue_declare(queue=QUEUE_NAME, durable=True, arguments={
    'x-dead-letter-exchange': DLX_NAME,  # Specify the DLX for the queue
    'x-delivery-limit': 3,  # Set max retry count to 3
    'x-queue-type': 'quorum'
})

# Bind your existing exchange to the DLX
channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key='')

print("Dead-letter exchange (DLX) and dead-letter queue (DLQ) setup completed.")
