import logging
import os
import json
from dotenv import load_dotenv
from amqpstorm import Connection
from amqpstorm import Message
from google.cloud import storage

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

# Initialize Google Cloud Storage client
storage_client = storage.Client()

# Get the public bucket URL
bucket_url = os.getenv('PUBLIC_BUCKET_URL')

for video_file in video_files:
    # Upload the video file to the public Google Cloud Storage bucket
    bucket_name = "staging-render-videos"  # Replace with your bucket name
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(f'input-videos/{video_file}')
    blob.upload_from_filename(f'./videos/{video_file}')

    # Generate the public URL for the uploaded video
    video_public_url = f'{bucket_url}/input-videos/{video_file}'

    # Update the folder and batch_name in base_params.json
    base_params['source_blob_name'] = f'input-videos/{video_file}'
    base_params['bucket_name'] = "staging-render-videos" 
    base_params['video_init_path'] = f"/content/drive/MyDrive/AI/StableDiffusion/InputVideos/{video_file}"
    
    # Update the folder and batch_name in base_params.json
    base_params['outdir'] = f"/content/drive/MyDrive/AI/StableDiffusion/Results/{video_file[:-4]}/"

    # Convert base_params to JSON string
    base_params_json = json.dumps(base_params)

    with Connection(rabbitmq_host, rabbitmq_username, rabbitmq_password) as connection:
        with connection.channel() as channel:
            # Declare the Queue, queue_name.
            channel.queue.declare(queue_name)

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
