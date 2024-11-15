import json
import os
import time
from threading import current_thread
import pika
import requests
from dotenv import load_dotenv

load_dotenv()
WORKER_SLEEP_TIME = int(os.getenv('WORKER_SLEEP_TIME'))

class Worker:
    def __init__(self, queue_name, host):
        self.thread_id = None
        self.queue_name = queue_name
        self.host = host

    def callback(self, ch, method, properties, body):
        print(f"Processing new request in thread {self.thread_id} for queue {self.queue_name}")
        # try:
        #     data = json.loads(body)
        #     url = data.get('url')
        #     body = data.get('body')
        #     time.sleep(10)
        #     response = requests.post(url, data=body, timeout=30)
        #
        #     if response.status_code == 200:
        #         print("sent request succesfully!")
        #         ch.basic_ack(delivery_tag=method.delivery_tag)
        #     else:
        #         print(f"Error processing request in thread {self.thread_id}")
        ch.basic_nack(delivery_tag=method.delivery_tag)
        # except Exception as e:
        #     print(f"Error processing request in thread {self.thread_id}: {str(e)}")
        #     # If processing failed due to an error, you can choose to not acknowledge
        #     ch.basic_nack(delivery_tag=method.delivery_tag)

    # Function to start consuming messages
    def start_consuming(self):
        self.thread_id = current_thread().name

        credentials = pika.PlainCredentials(username='username', password='password')
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, credentials=credentials))
        channel = connection.channel()

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback)

        try:
            channel.start_consuming()
        except Exception as e:
            print(f"Error in thread: {str(e)}")
