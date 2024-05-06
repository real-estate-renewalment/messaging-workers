import os
import threading
import schedule
from dotenv import load_dotenv
from worker import Worker

load_dotenv()

# RabbitMQ connection parameters
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
QUEUE_NAME = os.getenv('QUEUE_NAME')
INTERVAL = os.getenv('INTERVAL')
NUM_OF_THREADS = int(os.getenv('NUM_OF_THREADS'))


# Function to monitor and revive worker threads
def monitor_threads(num_of_threads):
    active_thread_count = sum(1 for thread in threading.enumerate() if thread.name.startswith("Thread-"))
    num_of_dead_threads = num_of_threads - active_thread_count
    while num_of_dead_threads > 0:
        print("a worker has died! starting a new one...")
        worker = Worker(QUEUE_NAME, RABBITMQ_HOST)
        worker_thread = threading.Thread(target=worker.start_consuming)
        worker_thread.start()
        num_of_dead_threads = num_of_threads - 1


if __name__ == "__main__":
    for i in range(NUM_OF_THREADS):
        worker = Worker(QUEUE_NAME, RABBITMQ_HOST)
        worker_thread = threading.Thread(target=worker.start_consuming, name=f'Thread-{i}')
        worker_thread.start()

    print("All workers are listening and ready for work")
    schedule.every(int(INTERVAL)).seconds.do(monitor_threads, NUM_OF_THREADS)

    while True:
        schedule.run_pending()
