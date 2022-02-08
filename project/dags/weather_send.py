# importing requests and json
import boto3
import requests

from datetime import datetime
def get_weather():
# base URL
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
    CITY = "Hickory"
    API_KEY = ""
    # upadting the URL
    URL = BASE_URL + "q=" + CITY + "&appid=" + API_KEY
    # HTTP request
    data = requests.get(URL)
    # getting data in the json format
    data_dict = data.json()
    

    sqs = boto3.resource('', region_name='',
                    aws_access_key_id="", 
                    aws_secret_access_key="")

    queue = sqs.get_queue_by_name(QueueName='weather')
    
    queue.send_message(MessageBody=f'{data_dict}')
    print('[x] Sent!')

