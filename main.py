import os
import threading
import schedule
from dotenv import load_dotenv
from worker import Worker

load_dotenv()

# RabbitMQ connection parameters
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
INTERVAL = os.getenv('INTERVAL')
NUM_OF_THREADS = int(os.getenv('NUM_OF_THREADS'))

# Define queue names for each type
QUEUE_NAMES = ["sms", "whatsapp", "mail"]

# Function to monitor and revive worker threads
def monitor_threads(num_of_threads):
    active_thread_count = sum(1 for thread in threading.enumerate() if thread.name.startswith("Thread-"))
    num_of_dead_threads = num_of_threads - active_thread_count
    while num_of_dead_threads > 0:
        print("A worker has died! Starting a new one...")
        # Determine which queue this worker should connect to based on current active thread count
        queue_name = QUEUE_NAMES[active_thread_count % len(QUEUE_NAMES)]
        worker = Worker(queue_name, RABBITMQ_HOST)
        worker_thread = threading.Thread(target=worker.start_consuming, name=f'Thread-{active_thread_count}')
        worker_thread.start()
        num_of_dead_threads -= 1


if __name__ == "__main__":
    for i in range(NUM_OF_THREADS):
        # Select queue based on the worker index, rotating among 'sms', 'whatsapp', and 'mail'
        queue_name = QUEUE_NAMES[i % len(QUEUE_NAMES)]
        worker = Worker(queue_name, RABBITMQ_HOST)
        worker_thread = threading.Thread(target=worker.start_consuming, name=f'Thread-{i}')
        worker_thread.start()

    print("All workers are listening and ready for work.")
    schedule.every(int(INTERVAL)).seconds.do(monitor_threads, NUM_OF_THREADS)

    while True:
        schedule.run_pending()
