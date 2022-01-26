import pika
import boto3
import requests
import spotipy.util as util


def send_queue():
    username = 'BigPapa'
    client_id = 'ce8d047b71eb4ba099b2ed70e5406f0c'
    client_secret = 'c25837880182401b9a890d0a3c9ddfd2'
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

    sqs = boto3.resource('sqs', region_name='us-east-1',
                    aws_access_key_id="AKIAZQL7U7P2KZDZG5HU", 
                    aws_secret_access_key="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")

    queue = sqs.get_queue_by_name(QueueName='spotify')
    
    queue.send_message(MessageBody=f'{song_data}')
    print('[x] Sent!')

