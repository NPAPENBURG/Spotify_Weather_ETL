import pika
import boto3
import requests
import spotipy.util as util


def send_queue():
    username = ''
    client_id = ''
    client_secret = ''
    redirect_uri = 'http://localhost:7777/callback'
    scope = 'user-read-recently-played'
    token = util.prompt_for_user_token(username=username,
                                       scope=scope,
                                       client_id=client_id,
                                       client_secret=client_secret,
                                       redirect_uri=redirect_uri)
    # Header for Spotify API
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {token}".format(token=token)
    }

    # Request to get recently played songs
    r = requests.get("https://api.spotify.com/v1/me/player/recently-played?", headers=headers)

    # saving the recently played songs into a json object
    song_data = r.json()

    sqs = boto3.resource('sqs', region_name='',
                    aws_access_key_id="", 
                    aws_secret_access_key="")

    queue = sqs.get_queue_by_name(QueueName='spotify')
    
    queue.send_message(MessageBody=f'{song_data}')
    print('[x] Sent!')

