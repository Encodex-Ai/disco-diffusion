import logging
import os
import json
from dotenv import load_dotenv
from amqpstorm import Connection
from amqpstorm import Message

logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv()

# Get the RabbitMQ connection details from environment variables
queue_name = os.getenv('RABBITMQ_QUEUE', 'simple_queue')
rabbitmq_host = os.getenv('RABBITMQ_HOST')
rabbitmq_username = os.getenv('RABBITMQ_USERNAME')
rabbitmq_password = os.getenv('RABBITMQ_PASSWORD')
rabbitmq_port = int(os.getenv('RABBITMQ_PORT', 5672))

# Load the base_params.json file
with open('params.json') as f:
    base_params = json.load(f)


# Get the list of video files in the folder
video_files = [filename for filename in os.listdir("./videos") if filename.endswith('.mp4')]
print("Found", len(video_files), "video files")

with Connection(rabbitmq_host, rabbitmq_username, rabbitmq_password) as connection:
    with connection.channel() as channel:
        # Declare the Queue, queue_name.
        channel.queue.declare(queue_name)

        for video_file in video_files:
            # Update the folder and batch_name in base_params.json
            base_params['folder'] = video_file
            base_params['batch_name'] = video_file

            # Convert base_params to JSON string
            base_params_json = json.dumps(base_params)

            # Message Properties.
            properties = {
                'content_type': 'application/json',
                'headers': {'key': 'value'}
            }

            # Create the message.
            message = Message.create(channel, base_params_json, properties)

            # Publish the message to a queue called, queue_name.
            message.publish(queue_name)
            print("Message sent for video:", video_file)
