# importing requests and json
import boto3
import requests

from datetime import datetime
def get_weather():
# base URL
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
    CITY = "Hickory"
    API_KEY = "cb9b93afbdaac3ce6e3230b3e0b8b05c"
    # upadting the URL
    URL = BASE_URL + "q=" + CITY + "&appid=" + API_KEY
    # HTTP request
    data = requests.get(URL)
    # getting data in the json format
    data_dict = data.json()
    

    sqs = boto3.resource('sqs', region_name='us-east-1',
                    aws_access_key_id="AKIAZQL7U7P2KZDZG5HU", 
                    aws_secret_access_key="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")

    queue = sqs.get_queue_by_name(QueueName='weather')
    
    queue.send_message(MessageBody=f'{data_dict}')
    print('[x] Sent!')

