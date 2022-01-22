import pika
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

    # Setting up RabbitMq Parameters
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='spotify-queue')

    channel.basic_publish(exchange='',
                          routing_key='spotify-queue',
                          body=str(song_data))
    print("[x] Sent")

    connection.close()
send_queue()